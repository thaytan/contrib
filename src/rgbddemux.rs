// Aivero
// Copyright (C) <2019> Aivero
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Library General Public
// License as published by the Free Software Foundation; either
// version 2 of the License, or (at your option) any later version.
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Library General Public License for more details.
// You should have received a copy of the GNU Library General Public
// License along with this library; if not, write to the
// Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
// Boston, MA 02110-1301, USA.

use glib::subclass;
use gst::prelude::*;
use gst::subclass::prelude::*;
use gst_depth_meta::rgbd;
use std::collections::HashMap;
use std::error::Error;
use std::fmt;
use std::fmt::{Display, Formatter};
use std::sync::{Mutex, RwLock};

lazy_static! {
    static ref CAT: gst::DebugCategory = gst::DebugCategory::new(
        "rgbddemux",
        gst::DebugColorFlags::empty(),
        Some("RGB-D Demuxer"),
    );
}

/// Default behaviour for distributing timestamps of the main buffer to the auxiliary buffers.
const DEFAULT_DISTRIBUTE_TIMESTAMPS: bool = false;

static PROPERTIES: [subclass::Property; 1] = [subclass::Property(
    "distribute-timestamps",
    |name| {
        glib::ParamSpec::boolean(
            name,
            "Distribute Timestamps",
            "If enabled, timestamps of the main buffers will be distributed to the auxiliary buffers embedded within the `video/rbgd` stream.",
            DEFAULT_DISTRIBUTE_TIMESTAMPS,
            glib::ParamFlags::READWRITE,
        )
    },
)];

#[derive(Debug, Clone)]
pub struct RgbdDemuxingError(pub String);
impl Error for RgbdDemuxingError {}
impl Display for RgbdDemuxingError {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "RgbdDemuxError: {:?}", self.0)
    }
}
impl From<RgbdDemuxingError> for gst::FlowError {
    fn from(error: RgbdDemuxingError) -> Self {
        gst_error!(CAT, "{:?}", error);
        gst::FlowError::Error
    }
}
/// Conversion from `gst::ErrorMessage` to RgbdDemuxingError.
impl From<gst::ErrorMessage> for RgbdDemuxingError {
    fn from(error: gst::ErrorMessage) -> RgbdDemuxingError {
        RgbdDemuxingError(format!("{}", error))
    }
}

/// A struct that identifies a stream.
struct StreamIdentifier {
    /// The id of the stream.
    stream_id: String,
    /// The group id of the stream.
    _group_id: gst::GroupId,
}

/// A handle on the pad, which contains information related to the pad.
struct PadHandle {
    /// The actual pad.
    pad: gst::Pad,
    /// A flag to indicate whether or not we have sent the "stream-start" event on the pad.
    has_pushed_stream_start: bool,
    /// The name of the stream flowing on the pad.
    stream_name: String,
}
impl PadHandle {
    /// Creates a new PadHandle for the given `pad`.
    /// # Arguments
    /// * `pad` - The pad to create a handle for.
    /// # Returns
    /// A new instance of [PadHandle](struct.PadHandle.html) for the pad.
    fn new(pad: gst::Pad) -> Self {
        let stream_name = pad.get_name().replace("src_", "");
        Self {
            pad,
            has_pushed_stream_start: false,
            stream_name,
        }
    }
}

type SrcPads = HashMap<String, PadHandle>;

/// A struct representation of the `rgbddemux` element
struct RgbdDemux {
    /// A mutex protecting an optional stream_id, which is set when the `rgbddemux` receives a
    /// stream-start.
    stream_id: Mutex<Option<StreamIdentifier>>,
    /// A hash map that associates stream tags (e.g. depth, infra1 etc.) with their associated pad.
    src_pads: RwLock<SrcPads>,
    /// Settings based on properties of the element
    settings: RwLock<Settings>,
    flow_combiner: Mutex<gst_base::UniqueFlowCombiner>,
}

/// A struct containing properties of `rgbddemux` element
struct Settings {
    /// Analogous to `distribute-timestamps` property
    distribute_timestamps: bool,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            distribute_timestamps: DEFAULT_DISTRIBUTE_TIMESTAMPS,
        }
    }
}

impl RgbdDemux {
    /// Pushes a "stream-start" event on the given pad.
    /// # Arguments
    /// * `pad` - The pad to push the event on.
    /// * `stream_identifier` - A stream identifier that uniquely identifies the current stream.
    /// * `stream_name` - A unique name of the stream to push a "stream-start" for.
    fn push_stream_start(pad: &gst::Pad, stream_identifier: &StreamIdentifier, stream_name: &str) {
        let stream_id = format!("{}/{}", stream_identifier.stream_id, stream_name);
        gst_debug!(CAT, "Pushing stream start event for stream {}", stream_id);

        // push a StreamStart event to tell downstream to expect output soon
        pad.push_event(
            gst::event::Event::new_stream_start(stream_id.as_str())
                .group_id(gst::util_group_id_next())
                .build(),
        );
    }

    /// Tries to push a "stream-start" event on the given `pad_handle`, if we have already gotten
    /// one from the upstream elements. If not, this function will do nothing.
    /// # Arguments
    /// * `pad_handle` - The pad we want to push the "stream-start" event on.
    /// * `stream_id` - The stream identifier, that uniquely identifies the current stream.
    /// * `name` - The name of the stream we want to push a "stream-start" for.
    fn try_push_stream_start_on_pad(
        pad_handle: &mut PadHandle,
        stream_id: Option<&StreamIdentifier>,
    ) {
        if !pad_handle.has_pushed_stream_start {
            if let Some(sid) = stream_id {
                Self::push_stream_start(&pad_handle.pad, sid, &pad_handle.stream_name);
                pad_handle.has_pushed_stream_start = true;
            }
        }
    }

    /// Pushes the "stream-start" event on all pads in `self.src_pads` that have not yet seen a
    /// "stream-start" event.
    /// # Arguments
    /// * `stream_identifier` - An instance of the [StreamIdentifier](struct.StreamIdentifier.html) struct that identifiers the stream we're currently working with.
    /// # Remarks
    /// * Requires `self.src_pads` to be exclusively locked for writing. Please ensure that it is
    /// unlocked when calling this function.
    fn push_stream_start_on_all_pads(&self, stream_identifier: &StreamIdentifier) {
        for (_, pad_handle) in self.src_pads.write().unwrap().iter_mut() {
            if !pad_handle.has_pushed_stream_start {
                Self::push_stream_start(
                    &pad_handle.pad,
                    &stream_identifier,
                    &pad_handle.stream_name,
                );
                pad_handle.has_pushed_stream_start = true;
            }
        }
    }

    /// Timestamps all auxiliary buffers with the timestamps found in the given `main_buffer`.
    /// # Arguments
    /// * `main_buffer` - A reference to the main `video/rgbd` buffer.
    fn timestamp_aux_buffers_from_main(main_buffer: &gst::Buffer) {
        // Get timestamp of the main buffer
        let common_pts = main_buffer.get_pts();
        let common_dts = main_buffer.get_dts();
        let common_duration = main_buffer.get_duration();

        // Get a mutable reference to the main buffer
        // Note: I could not figure out a better/easier way of doing that. Please let me know if you find some.
        let main_buffer_mut_ref = unsafe { gst::BufferRef::from_mut_ptr(main_buffer.as_mut_ptr()) };

        // Go through all auxiliary buffers
        for additional_buffer in &mut rgbd::get_aux_buffers_mut(main_buffer_mut_ref) {
            // Make the buffer mutable so that we can edit its timestamps
            let additional_buffer = additional_buffer.get_mut()
            .expect("rgbddemux: Cannot get mutable reference to an auxiliary buffer when distributing timestamps.");

            // Distribute the timestamp of the main buffer to the auxiliary buffers
            additional_buffer.set_pts(common_pts);
            additional_buffer.set_dts(common_dts);
            additional_buffer.set_duration(common_duration);
        }
    }

    /// Set the sink pad event and chain functions. This causes it to listen to GStreamer signals
    /// and take action correspondingly.
    /// Each function is wrapped in catch_panic_pad_function(), which will
    /// - Catch panics from the pad functions and instead of aborting the process
    ///   it will simply convert them into an error message and poison the element
    ///   instance
    /// - Extract RgbdDemux struct from the object instance and pass it to us
    /// # Arguments
    /// * `sink_pad` - The sink pad for which the signals should be listened to.
    fn set_sink_pad_functions(sink_pad: &gst::Pad) {
        // Sink Event
        sink_pad.set_event_function(|_, parent, event| {
            RgbdDemux::catch_panic_pad_function(
                parent,
                || false,
                |rgbd_demux, element| rgbd_demux.sink_event(element, event),
            )
        });
        // Sink Chain
        sink_pad.set_chain_function(|_, parent, buffer| {
            RgbdDemux::catch_panic_pad_function(
                parent,
                || Err(gst::FlowError::Error),
                |rgbd_demux, element| rgbd_demux.sink_chain(element, buffer),
            )
        });
    }

    /// Called whenever an event is received at the sink pad. CAPS and stream start events will be
    /// handled locally, all other events are send further downstream.
    /// # Arguments
    /// * `element` - The element that represents the `rgbddemux` in GStreamer.
    /// * `event` - The event that should be handled.
    fn sink_event(&self, element: &gst::Element, event: gst::Event) -> bool {
        use gst::EventView;
        gst_debug!(CAT, obj: element, "Got a new event: {:?}", event);

        match event.view() {
            EventView::Caps(caps) => {
                gst_debug!(CAT, obj: element, "Got a new caps event: {:?}", caps);
                // Call function that creates src pads according to the received Caps event
                match self.renegotiate_downstream_caps(element, caps.get_caps()) {
                    Ok(_) => {
                        gst_debug!(CAT, "Caps successfully renegotiated");
                        true
                    }
                    Err(e) => {
                        gst_error!(CAT, obj: element, "{}", e);
                        false
                    }
                }
            }
            EventView::StreamStart(stream_start) => {
                gst_debug!(CAT, "Got a stream start event {:?}", stream_start);
                let stream_identifier = StreamIdentifier {
                    stream_id: stream_start.get_stream_id().to_string(),
                    _group_id: stream_start.get_group_id(),
                };

                self.push_stream_start_on_all_pads(&stream_identifier);

                *self.stream_id.lock().unwrap() = Some(stream_identifier);

                // Accept any StreamStart event
                true
            }
            _ => {
                // By default, pass any other event to all src pads
                let src_pads = &self.src_pads.read().unwrap();
                if src_pads.is_empty() {
                    // Return false if there is no src pad yet since this element does not handle it
                    return false;
                }

                src_pads.values().all(|p| p.pad.push_event(event.clone()))
            }
        }
    }

    /// Create additional src pads, which happens as a result of a CAPS renegotiation.
    /// # Arguments
    /// * `element` - The element that represents `rgbddemux` in GStreamer.
    /// * `rgbd_caps` - The CAPS that we should create src pads for.
    fn renegotiate_downstream_caps(
        &self,
        element: &gst::Element,
        rgbd_caps: &gst::CapsRef,
    ) -> Result<(), RgbdDemuxingError> {
        gst_debug!(CAT, "renegotiate_downstream_caps");
        // Extract the `video/rgbd` caps fields from gst::CapsRef
        let rgbd_caps = rgbd_caps.iter().next().ok_or_else(|| {
            RgbdDemuxingError(
                "Invalid `video/rgbd` caps for creation of additional src pads".to_string(),
            )
        })?;

        // Determine what streams are contained within the caps            )
        let streams = rgbd_caps
            .get::<String>("streams")
            .or_else(|err| {
                Err(RgbdDemuxingError(format!(
                    "No `streams` field detected in `video/rgbd` caps: {:?}",
                    err
                )))
            })?
            .unwrap_or_default();
        let streams = streams.split(',').collect::<Vec<&str>>();

        if streams.is_empty() {
            return Err(RgbdDemuxingError(
                "Cannot detect any streams in `video/rgbd` caps under field `streams`".to_string(),
            ));
        }

        // Get a common framerate for all streams
        let common_framerate = rgbd_caps
            .get_some::<gst::Fraction>("framerate")
            .or_else(|err| {
                Err(RgbdDemuxingError(format!(
                    "Cannot detect any `framerate` in `video/rgbd` caps: {:?}",
                    err
                )))
            })?;

        // Iterate over all streams, find their caps and push a CAPS negotiation event
        let mut src_pads = self.src_pads.write().unwrap();
        let mut flow_combiner = self.flow_combiner.lock().unwrap();
        for stream_name in streams.iter() {
            // Determine the appropriate caps for the stream
            let new_pad_caps = if stream_name.contains("meta") {
                gst_info!(CAT, obj: element, "Got meta of name: {}", stream_name);
                // Get `video/meta-klv` caps if the `meta` stream is enabled
                gst::Caps::new_simple("meta/x-klv", &[("parsed", &true)])
            } else {
                self.extract_stream_caps(stream_name, &rgbd_caps, common_framerate)?
            };

            let pad_name = format!("src_{}", stream_name);
            let pad_handle = match src_pads.get_mut(&pad_name) {
                Some(p) => p,
                None => {
                    Self::create_new_src_pad(
                        element,
                        &mut *src_pads,
                        &mut *flow_combiner,
                        stream_name,
                        None,
                    );
                    src_pads.get_mut(&pad_name).unwrap()
                }
            };

            Self::try_push_stream_start_on_pad(pad_handle, self.stream_id.lock().unwrap().as_ref());

            // And a CAPS, so they know what they're dealing with
            gst_debug!(CAT, "Pushing new caps event");
            pad_handle
                .pad
                .push_event(gst::event::Event::new_caps(&new_pad_caps).build());
            gst_debug!(CAT, "All done from here");
        }
        Ok(())
    }

    /// Extract CAPS for the given stream from the given rgbd_caps.
    /// # Arguments
    /// * `stream_name` - The name of the stream to extract CAPS for, e.g. `depth`.
    /// * `rgbd_caps` - A reference to the `video/rgbd` CAPS, from which the stream's CAPS should be extracted.
    /// * `common_framerate` - The framerate of all the streams.
    fn extract_stream_caps(
        &self,
        stream_name: &str,
        rgbd_caps: &gst::StructureRef,
        common_framerate: gst::Fraction,
    ) -> Result<gst::Caps, RgbdDemuxingError> {
        // TODO: return "image/jpeg" CAPS if the CAPS type is "image/jpeg" (in addition to "video/x-raw" with "*jpeg*" as "format" of the stream)

        // Get the format of a stream
        let stream_format = rgbd_caps
            .get::<String>(&format!("{}_format", stream_name))
            .or_else(|err| {
                Err(RgbdDemuxingError(format!(
                    "Cannot detect any `format` in `video/rgbd` caps for `{}` stream: {:?}",
                    stream_name, err
                )))
            })?
            .unwrap_or_default();

        // Return "image/jpeg" CAPS if the format is MJPG
        if stream_format.contains("jpeg") {
            return Ok(gst::Caps::new_simple("image/jpeg", &[]));
        }

        // Get the width of a stream
        let stream_width = rgbd_caps
            .get_some::<i32>(&format!("{}_width", stream_name))
            .or_else(|err| {
                Err(RgbdDemuxingError(format!(
                    "Cannot detect any `width` in `video/rgbd` caps for `{}` stream: {:?}",
                    stream_name, err
                )))
            })?;

        // Get the height of a stream
        let stream_height = rgbd_caps
            .get_some::<i32>(&format!("{}_height", stream_name))
            .or_else(|err| {
                Err(RgbdDemuxingError(format!(
                    "Cannot detect any `height` in `video/rgbd` caps for `{}` stream: {:?}",
                    stream_name, err
                )))
            })?;

        // Create caps for the new src pad
        Ok(gst::Caps::new_simple(
            "video/x-raw",
            &[
                ("format", &stream_format),
                ("width", &stream_width),
                ("height", &stream_height),
                ("framerate", &common_framerate),
            ],
        ))
    }

    /// Create a new src pad on the `rgbddemux` for the stream with the given name.
    /// # Arguments
    /// * `element` - The element that represents the `rgbddemux` in GStreamer.
    /// * `src_pads` - A mutable reference to the collection of pads currently present on the `rgbddemux`.
    /// * `flow_combiner` - A mutable reference to the flow combiner that drives the `rgbddemux`.
    /// * `stream_name` - The name of the stream to create a src pad for.
    /// * `template` - An optional template to use on the pod.
    fn create_new_src_pad(
        element: &gst::Element,
        src_pads: &mut SrcPads,
        flow_combiner: &mut gst_base::UniqueFlowCombiner,
        stream_name: &str,
        template: Option<gst::PadTemplate>,
    ) {
        gst_debug!(CAT, obj: element, "create_new_src_pad for {}", stream_name);

        // Create naming for the src pad according to the stream
        let new_src_pad_name = &format!("src_{}", stream_name);

        // In case such pad already exists we return None, as only one pad for each stream type may existing
        // If the pad has been generated by the CAPS and has previously been requested (such as in
        // gst-launch), the calling function must ensure to check if the pads exist before calling this function.
        // This scenario can happen when:
        // - gst-launch rbgddemux name=d d.src_depth ! ... d.src_depth ! ...
        // - An application calls request_pad with the same name twice
        if src_pads.contains_key(new_src_pad_name) {
            gst_error!(
                CAT,
                obj: element,
                "Pad `{}` already exists. Only one pad for each stream may be requested",
                new_src_pad_name
            );
            return;
        }

        // Create the src pad with these caps
        let new_src_pad = gst::Pad::new_from_template(
            &template.unwrap_or_else(|| {
                element
                    .get_pad_template("src_%s")
                    .expect("No src pad template registered in rgbddemux")
            }),
            Some(new_src_pad_name),
        );

        // Add the src pad to the element and activate it
        element
            .add_pad(&new_src_pad)
            .expect("Could not add src pad in rgbddemux");
        new_src_pad
            .set_active(true)
            .expect("Could not activate new src pad in rgbddemux");

        // Add the new pad to the internals
        flow_combiner.add_pad(&new_src_pad);
        src_pads.insert(new_src_pad_name.to_string(), PadHandle::new(new_src_pad));
        gst_debug!(CAT, "Pad created");
    }

    /// Called whenever a new buffer is passed to the sink pad. This function splits the buffer in
    /// to multiple buffer, which are pushed on their corresponding src pad.
    /// # Arguments
    /// * `element` - The element that represents the `rgbddemux` in GStreamer.
    /// * `main_buffer` - The buffer that was received on the sink pad.
    fn sink_chain(
        &self,
        element: &gst::Element,
        main_buffer: gst::Buffer,
    ) -> Result<gst::FlowSuccess, gst::FlowError> {
        // Lock the internals
        let settings = self
            .settings
            .read()
            .expect("Failed to lock internals in rgbddemux");

        // Distribute the timestamp of the main buffer to the auxiliary buffers, if enabled
        if settings.distribute_timestamps {
            Self::timestamp_aux_buffers_from_main(&main_buffer);
        }

        // Go through all auxiliary buffers attached to the main buffer in order to extract them and
        // push to the corresponding src pads
        let src_pads = self.src_pads.read().unwrap();
        for additional_buffer in rgbd::get_aux_buffers(&main_buffer) {
            // Push the additional buffer to the corresponding src pad
            let _flow_combiner_result = self.flow_combiner.lock().unwrap().update_flow(
                self.push_buffer_to_corresponding_pad(&*src_pads, additional_buffer)
                    .map_err(|e| {
                        gst_warning!(CAT, obj: element, "Failed to push a stacked buffer: {}", e);
                        gst::FlowError::Error
                    }),
            );
        }

        gst_debug!(
            CAT,
            obj: element,
            "All meta buffers have been pushed. Now pushing a buffer, tagged: {:?}:",
            rgbd::get_tag(&main_buffer)
        );

        // Push the main buffer to the corresponding src pad
        let _ignore = self.flow_combiner.lock().unwrap().update_flow(
            self.push_buffer_to_corresponding_pad(&*src_pads, main_buffer)
                .map_err(|e| {
                    gst_warning!(CAT, obj: element, "Failed to push a main buffer: {}", e);
                    gst::FlowError::Error
                }),
        ); // removing ; means fail if we cannot push main buffer.
        Ok(gst::FlowSuccess::Ok)
    }

    /// Push the given buffer to the src pad that was allocated for it.
    /// # Arguments
    /// * `element` - The element that represents the `rgbddemux` in GStreamer.
    /// * `src_pads` - A hash map that associates buffer title tags with their corresponding pad.
    /// * `buffer` - The buffer that should be pushed further downstream.
    fn push_buffer_to_corresponding_pad(
        &self,
        src_pads: &HashMap<String, PadHandle>,
        buffer: gst::Buffer,
    ) -> Result<gst::FlowSuccess, RgbdDemuxingError> {
        // Extract tag title from the buffer
        let tag_title = rgbd::get_tag(&buffer)?;

        // Match the tag title with a corresponding src pad
        let src_pad = src_pads
            .get(&(format!("src_{}", tag_title)))
            .ok_or_else(|| {
                RgbdDemuxingError(format!(
                    "No corresponding pad for buffer with tag title `{}` exists",
                    tag_title
                ))
            })?;

        // Check if there's a per-frame metadata buffer we need to push to the meta pad
        gst_debug!(CAT, "Pushing per-frame meta for {}", tag_title);

        src_pad.pad.push(buffer).map_err(|_| {
            RgbdDemuxingError("Failed to push buffer onto its corresponding pad".to_string())
        })
    }
}

impl ObjectSubclass for RgbdDemux {
    const NAME: &'static str = "rgbddemux";
    type ParentType = gst::Element;
    type Instance = gst::subclass::ElementInstanceStruct<Self>;
    type Class = subclass::simple::ClassStruct<Self>;

    glib_object_subclass!();

    fn new() -> Self {
        Self {
            src_pads: RwLock::new(HashMap::new()),
            flow_combiner: Mutex::new(gst_base::UniqueFlowCombiner::new()),
            settings: RwLock::new(Settings::default()),
            stream_id: Mutex::new(None),
        }
    }

    fn class_init(klass: &mut subclass::simple::ClassStruct<Self>) {
        klass.set_metadata(
            "RGB-D Demuxer",
            "Demuxer/RGB-D",
            "Demuxes  a single `video/rgbd` into multiple `video/x-raw`",
            "Raphael Dürscheid <rd@aivero.com>, Andrej Orsula <andrej.orsula@aivero.com>, Tobias Morell <tobias.morell@aivero.com>",
        );

        klass.install_properties(&PROPERTIES);

        // src pads
        let mut src_caps = gst::Caps::new_simple("video/x-raw", &[]);
        {
            let src_caps = src_caps
                .get_mut()
                .expect("Could not get mutable reference to src_caps");
            src_caps.append(gst::Caps::new_simple("meta/x-klv", &[("parsed", &true)]));
            src_caps.append(gst::Caps::new_simple("image/jpeg", &[]));
        }

        klass.add_pad_template(
            gst::PadTemplate::new(
                "src_%s",
                gst::PadDirection::Src,
                gst::PadPresence::Request,
                &src_caps,
            )
            .expect("Failed to add src pad template in rgbddemux"),
        );

        // sink pad
        klass.add_pad_template(
            gst::PadTemplate::new(
                "sink",
                gst::PadDirection::Sink,
                gst::PadPresence::Always,
                &gst::Caps::new_simple("video/rgbd", &[]),
            )
            .expect("Failed to add sink pad template in rgbddemux"),
        );
    }
}

impl ObjectImpl for RgbdDemux {
    glib_object_impl!();

    fn constructed(&self, obj: &glib::Object) {
        self.parent_constructed(obj);
        let element = obj
            .downcast_ref::<gst::Element>()
            .expect("Failed to cast `obj` to a gst::Element");

        // Create sink pad from the template that is registered with the class
        let templ = element
            .get_pad_template("sink")
            .expect("Failed to get sink pad template in rgbddemux");
        let sink_pad = gst::Pad::new_from_template(&templ, Some("sink"));

        // Set all sink pad functions
        Self::set_sink_pad_functions(&sink_pad);

        // Add the sink pad to the element
        element
            .add_pad(&sink_pad)
            .expect("Failed to add sink pad in rgbddemux");
    }

    fn set_property(&self, obj: &glib::Object, id: usize, value: &glib::Value) {
        let element = obj
            .downcast_ref::<gst::Element>()
            .expect("Failed to cast `obj` to a gst::Element");
        let mut settings = self
            .settings
            .write()
            .expect("rgbddemux: Could not lock internals to access settings in `set_property()`");

        let property = &PROPERTIES[id];
        match *property {
            subclass::Property("distribute-timestamps", ..) => {
                let distribute_timestamps = value.get_some().unwrap_or_else(|err| panic!("rgbddemux: Failed to set property `distribute-timestamps` due to incorrect type: {:?}", err));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `distribute-timestamps` from {} to {}",
                    settings.distribute_timestamps,
                    distribute_timestamps
                );
                settings.distribute_timestamps = distribute_timestamps;
            }
            _ => unimplemented!("Property is not implemented"),
        };
    }

    fn get_property(&self, _obj: &glib::Object, id: usize) -> Result<glib::Value, ()> {
        let settings = &self
            .settings
            .read()
            .expect("rgbddemux: Could not lock internals to access settings in `set_property()`");

        let prop = &PROPERTIES[id];
        match *prop {
            subclass::Property("distribute-timestamps", ..) => {
                Ok(settings.distribute_timestamps.to_value())
            }
            _ => unimplemented!("Property is not implemented"),
        }
    }
}

impl ElementImpl for RgbdDemux {
    /// This function is called when a peer element requests a pad on the element. It is used to
    /// provide a custom implementation for creating new pads.
    /// An example where this function is called is using the `.` operator in gst-launch, e.g.
    /// `rbgddemux name=d d.src_depth ! colorizer ...`.
    /// # Arguments
    /// * `element` - The element, which represents the `rgbddemux` in GStreamer.
    /// * `templ` - The pad template that should be used for the pad.
    /// * `name` - An optional name for the pad.
    /// * `_caps` - (not used) The CAPS that should be used for the pad. Currently the `rgbddemux` solely generated src pad CAPS from the rgbd CAPS.
    fn request_new_pad(
        &self,
        element: &gst::Element,
        templ: &gst::PadTemplate,
        name: Option<String>,
        _caps: Option<&gst::Caps>,
    ) -> Option<gst::Pad> {
        gst_debug!(CAT, obj: element, "Requesting new pad with name {:?}", name);
        // Get the pads name and reject any requests that are not for src pads
        let name = name?;
        if !name.starts_with("src_") {
            gst_error!(
                CAT,
                obj: element,
                "Only source pads may be created on request."
            );
            return None;
        }

        // Create a new pad and return it
        let mut src_pads = self.src_pads.write().unwrap();
        Self::create_new_src_pad(
            element,
            &mut *src_pads,
            &mut *self.flow_combiner.lock().unwrap(),
            &name[4..], // strip the src_ away
            Some(templ.clone()),
        );

        let pad_handle = src_pads.get_mut(&*name)?;
        Self::try_push_stream_start_on_pad(pad_handle, self.stream_id.lock().unwrap().as_ref());

        gst_debug!(CAT, "Pad request succeeded");
        Some(pad_handle.pad.clone())
    }
}

pub fn register(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    gst::Element::register(
        Some(plugin),
        "rgbddemux",
        gst::Rank::None,
        RgbdDemux::get_type(),
    )
}
