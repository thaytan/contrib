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
use gst_depth_meta::{rgbd, BufferMeta};
use std::collections::HashMap;
use std::sync::{Mutex, RwLock};

use super::demux_pad::*;
use super::error::*;
use super::properties::*;
use super::stream_identifier::*;
use crate::common::*;

lazy_static! {
    /// Debug category for 'rgbddemux' element.
    pub(crate) static ref CAT: gst::DebugCategory = gst::DebugCategory::new(
        "rgbddemux",
        gst::DebugColorFlags::empty(),
        Some("RGB-D Demuxer"),
    );
}

/// Hashmap of source pads of the demuxer, where key is the name of the stream flowing through that pad.
pub type SrcPads = HashMap<String, DemuxPad>;

/// A struct representation of the `rgbddemux` element.
struct RgbdDemux {
    /// Settings based on properties of the element.
    settings: RwLock<Settings>,
    /// List of source pads on this demuxer.
    src_pads: RwLock<SrcPads>,
    /// Utility struct that handles GstFlowReturn combinations with multiple source pads.
    flow_combiner: Mutex<gst_base::UniqueFlowCombiner>,
    /// Utility struct that contains stream and group id, used when pushing stream-start events.
    stream_identifier: Mutex<Option<StreamIdentifier>>,
}

impl ObjectSubclass for RgbdDemux {
    const NAME: &'static str = "rgbddemux";
    type ParentType = gst::Element;
    type Instance = gst::subclass::ElementInstanceStruct<Self>;
    type Class = subclass::simple::ClassStruct<Self>;

    glib_object_subclass!();

    fn new() -> Self {
        Self {
            settings: RwLock::new(Settings::default()),
            src_pads: RwLock::new(HashMap::new()),
            flow_combiner: Mutex::new(gst_base::UniqueFlowCombiner::new()),
            stream_identifier: Mutex::new(None),
        }
    }

    fn class_init(klass: &mut subclass::simple::ClassStruct<Self>) {
        klass.set_metadata(
            "RGB-D Demuxer",
            "Demuxer/RGB-D",
            "Demuxes a single `video/rgbd` stream into multiple elementary streams",
            "Raphael Dürscheid <rd@aivero.com>, Andrej Orsula <andrej.orsula@aivero.com>, Tobias Morell <tobias.morell@aivero.com>",
        );

        klass.install_properties(&PROPERTIES);

        // Src pads
        let mut src_caps = gst::Caps::new_simple("video/x-raw", &[]);
        {
            let src_caps = src_caps.get_mut().unwrap();
            src_caps.append(gst::Caps::new_simple("meta/x-klv", &[("parsed", &true)]));
            src_caps.append(gst::Caps::new_simple("image/jpeg", &[]));
        }

        klass.add_pad_template(
            gst::PadTemplate::new(
                "src_%s",
                gst::PadDirection::Src,
                gst::PadPresence::Sometimes,
                &src_caps,
            )
            .expect("rgbddemux: Failed to add 'src_%s' pad template"),
        );

        // Sink pad
        klass.add_pad_template(
            gst::PadTemplate::new(
                "sink",
                gst::PadDirection::Sink,
                gst::PadPresence::Always,
                &gst::Caps::new_simple("video/rgbd", &[]),
            )
            .expect("rgbddemux: Failed to add 'sink' pad template"),
        );
    }
}

impl ElementImpl for RgbdDemux {
    fn change_state(
        &self,
        element: &::gst::Element,
        transition: gst::StateChange,
    ) -> Result<gst::StateChangeSuccess, gst::StateChangeError> {
        #[allow(clippy::single_match)]
        match transition {
            gst::StateChange::PausedToReady => {
                // Reset internals (except for settings)
                self.flow_combiner.lock().unwrap().reset();
                *self.stream_identifier.lock().unwrap() = None;
                // Reset stream start tracker, but keep the pads
                for (_, src_pad) in self.src_pads.write().unwrap().iter_mut() {
                    src_pad.pushed_stream_start = false;
                }
            }
            _ => {}
        }

        // Chain up parent implementation
        self.parent_change_state(element, transition)
    }
}

impl RgbdDemux {
    /// Called whenever an event is received at the sink pad. CAPS and stream start events will be
    /// handled locally, all other events are send further downstream.
    /// # Arguments
    /// * `element` - The element that represents the `rgbddemux` in GStreamer.
    /// * `event` - The event that should be handled.
    fn sink_event(&self, element: &gst::Element, event: gst::Event) -> bool {
        use gst::EventView;
        match event.view() {
            EventView::Caps(caps) => {
                gst_debug!(CAT, obj: element, "Got a new caps event: {:?}", caps);
                // Create src pads according to the received upstream CAPS
                match self.create_src_pads_from_sink_caps(element, caps.get_caps()) {
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
                    group_id: stream_start
                        .get_group_id()
                        .unwrap_or_else(gst::GroupId::next),
                };

                // Pass stream start event on all existing src pads
                self.push_stream_start_on_all_pads(&stream_identifier);

                // Update internals with the new stream identifier
                *self.stream_identifier.lock().unwrap() = Some(stream_identifier);

                // Accept any StreamStart event
                true
            }
            _ => {
                gst_debug!(CAT, obj: element, "Got a new event: {:?}", event);
                let sink_pad = element.get_static_pad("sink").unwrap();
                sink_pad.event_default(Some(element), event)
            }
        }
    }

    /// Create additional src pads, which happens as a result of a CAPS renegotiation.
    /// # Arguments
    /// * `element` - The element that represents `rgbddemux` in GStreamer.
    /// * `rgbd_caps` - The sink CAPS that we should create src pads for.
    fn create_src_pads_from_sink_caps(
        &self,
        element: &gst::Element,
        rgbd_caps: &gst::CapsRef,
    ) -> Result<(), RgbdDemuxError> {
        gst_debug!(
            CAT,
            "Creating new src pads based on the negotiated upstream CAPS"
        );

        // Extract the `video/rgbd` caps fields from gst::CapsRef
        let rgbd_caps = rgbd_caps.iter().next().ok_or_else(|| {
            RgbdDemuxError(
                "Invalid `video/rgbd` caps for creation of additional src pads".to_string(),
            )
        })?;

        // Determine what streams are contained within the caps
        let streams = rgbd_caps
            .get::<String>("streams")
            .map_err(|err| {
                RgbdDemuxError(format!(
                    "No `streams` field detected in `video/rgbd` caps: {:?}",
                    err
                ))
            })?
            .unwrap_or_default();
        let streams = streams.split(',').collect::<Vec<&str>>();
        if streams.is_empty() {
            return Err(RgbdDemuxError(
                "Cannot detect any streams in `video/rgbd` caps under field `streams`".to_string(),
            ));
        }

        // Get a common framerate for all streams
        let common_framerate = rgbd_caps
            .get_some::<gst::Fraction>("framerate")
            .map_err(|err| {
                RgbdDemuxError(format!(
                    "Cannot detect any `framerate` in `video/rgbd` caps: {:?}",
                    err
                ))
            })?;

        let mut src_pads = self.src_pads.write().unwrap();

        // Remove pads that are no longer needed for the new CAPS
        Self::remove_unneeded_pads(element, &mut src_pads, &streams);

        // Iterate over all streams, find their caps and push a CAPS negotiation event
        let mut flow_combiner = self.flow_combiner.lock().unwrap();
        for stream_name in streams.iter() {
            // Determine the appropriate caps for the stream
            let new_pad_caps =
                self.extract_stream_caps(stream_name, &rgbd_caps, common_framerate)?;

            self.create_new_src_pad(
                element,
                &mut src_pads,
                &mut flow_combiner,
                stream_name,
                new_pad_caps,
            );
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
    ) -> Result<gst::Caps, RgbdDemuxError> {
        // Return "meta/x-klv" if we are dealing with metadata stream
        if stream_name.contains("meta") {
            return Ok(gst::Caps::new_simple("meta/x-klv", &[("parsed", &true)]));
        };

        // Get the format of a stream
        let stream_format = rgbd_caps
            .get::<String>(&format!("{}_format", stream_name))
            .map_err(|err| {
                RgbdDemuxError(format!(
                    "Cannot detect any `format` in `video/rgbd` caps for `{}` stream: {:?}",
                    stream_name, err
                ))
            })?
            .unwrap_or_default();

        // Return "image/jpeg" CAPS if the format is MJPG
        if stream_format.contains("jpeg") {
            return Ok(gst::Caps::new_simple("image/jpeg", &[]));
        }

        // Get the width of a stream
        let stream_width = rgbd_caps
            .get_some::<i32>(&format!("{}_width", stream_name))
            .map_err(|err| {
                RgbdDemuxError(format!(
                    "Cannot detect any `width` in `video/rgbd` caps for `{}` stream: {:?}",
                    stream_name, err
                ))
            })?;

        // Get the height of a stream
        let stream_height = rgbd_caps
            .get_some::<i32>(&format!("{}_height", stream_name))
            .map_err(|err| {
                RgbdDemuxError(format!(
                    "Cannot detect any `height` in `video/rgbd` caps for `{}` stream: {:?}",
                    stream_name, err
                ))
            })?;

        // Create caps for the new "video/x-raw" src pad
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

    /// Remove pads from `src_pads` that are no longer needed in a set of `allowed_streams`.
    /// Note that this function removes the pads both from element and `src_pads`.
    /// # Arguments
    /// * `element` - The element that represents `rgbddemux` in GStreamer.
    /// * `src_pads` - List of current source pads.
    /// * `allowed_streams` - List of allowed streams, e.g. based on upstream CAPS.
    fn remove_unneeded_pads(
        element: &gst::Element,
        src_pads: &mut SrcPads,
        allowed_streams: &[&str],
    ) {
        src_pads.retain(|stream_name, src_pad| {
            if !allowed_streams
                .iter()
                .any(|&caps_stream| caps_stream == stream_name)
            {
                gst_debug!(
                    CAT,
                    obj: element,
                    "Removing pad for {} stream as it is no longer needed in the newly negotiated streams {:?}",
                    stream_name, allowed_streams
                );

                // De-activate the pad
                src_pad.pad.set_active(false).unwrap_or_else(|_| {
                    panic!("Could not deactivate a src pad: {:?}", src_pad.pad)
                });

                // Remove the pad from the element
                element
                    .remove_pad(&src_pad.pad)
                    .unwrap_or_else(|_| panic!("Could not remove a src pad: {:?}", src_pad.pad));

                false
            } else {
                true
            }
        });
    }

    /// Create a new src pad on the `rgbddemux` for the stream with the given name.
    /// This function won't create a pad if it already exists.
    /// # Arguments
    /// * `element` - The element that represents the `rgbddemux` in GStreamer.
    /// * `src_pads` - A mutable reference to the collection of pads currently present on the `rgbddemux`.
    /// * `flow_combiner` - A mutable reference to the flow combiner that drives the `rgbddemux`.
    /// * `stream_name` - The name of the stream to create a src pad for.
    fn create_new_src_pad(
        &self,
        element: &gst::Element,
        src_pads: &mut SrcPads,
        flow_combiner: &mut gst_base::UniqueFlowCombiner,
        stream_name: &str,
        new_pad_caps: gst::Caps,
    ) {
        gst_debug!(
            CAT,
            obj: element,
            "Creating new src pad for {} stream",
            stream_name
        );

        // Create naming for the src pad according to the stream
        let new_src_pad_name = &format!("src_{}", stream_name);

        // Do not create a new pad if it already exists
        if src_pads.contains_key(stream_name) {
            gst_info!(
                CAT,
                obj: element,
                "Pad `{}` was already created during previous CAPS negotiation with upstream element",
                new_src_pad_name
            );
            return;
        }

        // Create the src pad based on template
        let pad = gst::Pad::from_template(
            &element
                .get_pad_template("src_%s")
                .expect("rgbdmux: No 'src_%s' pad template registered"),
            Some(new_src_pad_name),
        );

        // Add the pad to the element
        element
            .add_pad(&pad)
            .expect("rgbdmux: Could not add src pad to the element");

        // Create a DemuxPad from it
        let mut pad_handle = DemuxPad::new(pad);

        // Push stream-start event to indicate beginning of the stream
        if let Some(stream_identifier) = self.stream_identifier.lock().unwrap().as_ref() {
            Self::push_stream_start(&mut pad_handle, stream_name, &stream_identifier);
        }

        // Push CAPS event, so that downstream element know what data they're dealing with
        gst_debug!(CAT, "Pushing a new caps event for {} stream", stream_name);
        pad_handle
            .pad
            .push_event(gst::event::Caps::builder(&new_pad_caps).build());

        // Activate the pad
        pad_handle
            .pad
            .set_active(true)
            .expect("rgbdmux: Could not activate new src pad");

        // Finally, add the new pad to the internals
        flow_combiner.add_pad(&pad_handle.pad);
        src_pads.insert(stream_name.to_string(), pad_handle);

        gst_debug!(
            CAT,
            "New pad for {} stream successfuly created",
            stream_name
        );
    }

    /// Called whenever a new buffer is passed to the sink pad. This function splits the buffer in
    /// to multiple buffer, which are pushed on their corresponding src pad.
    /// # Arguments
    /// * `element` - The element that represents the `rgbddemux` in GStreamer.
    /// * `main_buffer` - The buffer that was received on the sink pad.
    fn sink_chain(
        &self,
        element: &gst::Element,
        mut main_buffer: gst::Buffer,
    ) -> Result<gst::FlowSuccess, gst::FlowError> {
        // Distribute the timestamp of the main buffer to the auxiliary buffers, if enabled
        if self.settings.read().unwrap().distribute_timestamps {
            Self::timestamp_aux_buffers_from_main(main_buffer.make_mut());
        }

        gst_trace!(
            CAT,
            obj: element,
            "Pushing buffers to their corresponding pads",
        );

        // Go through all auxiliary buffers attached to the main buffer in order to extract them and
        // push to the corresponding src pads
        let src_pads = self.src_pads.read().unwrap();
        let mut flow_combiner = self.flow_combiner.lock().unwrap();
        for aux_buffer in rgbd::get_aux_buffers(&main_buffer) {
            let flow_combiner_result = flow_combiner.update_flow(
                self.push_buffer_to_corresponding_pad(element, &src_pads, aux_buffer)
                    .map_err(|e| {
                        gst_warning!(CAT, obj: element, "Failed to push auxiliary buffers: {}", e);
                        gst::FlowError::Error
                    }),
            );
            if flow_combiner_result.is_err() {
                return flow_combiner_result;
            }
        }

        // Push the main buffer to the corresponding src pad
        flow_combiner.update_flow(
            self.push_buffer_to_corresponding_pad(element, &src_pads, main_buffer)
                .map_err(|e| {
                    gst_warning!(CAT, obj: element, "Failed to push main buffer: {}", e);
                    gst::FlowError::Error
                }),
        )
    }

    /// Push the given buffer to the src pad that was allocated for it.
    /// # Arguments
    /// * `element` - The element that represents the `rgbddemux` in GStreamer.
    /// * `src_pads` - A hash map that associates buffer title tags with their corresponding pad.
    /// * `buffer` - The buffer that should be pushed further downstream.
    fn push_buffer_to_corresponding_pad(
        &self,
        element: &gst::Element,
        src_pads: &HashMap<String, DemuxPad>,
        buffer: gst::Buffer,
    ) -> Result<gst::FlowSuccess, RgbdDemuxError> {
        // Extract tag title from the buffer
        let tag_title = rgbd::get_tag(&buffer)?;

        // Match the tag title with a corresponding src pad
        if let Some(src_pad) = src_pads.get(&tag_title) {
            // Do not attempt to push buffers, if pad is not linked
            if !src_pad.pad.is_linked() {
                gst_debug!(
                    CAT,
                    obj: element,
                    "Buffer {} is not pushed because its pad is not linked",
                    tag_title
                );
                return Ok(gst::FlowSuccess::Ok);
            }

            // Attempt to push a buffer to the pad
            gst_trace!(
                CAT,
                obj: element,
                "Pushing buffer for stream {} to the corresponding pad",
                tag_title
            );
            src_pad.pad.push(buffer).map_err(|_| {
                RgbdDemuxError("Failed to push buffer onto its corresponding pad".to_string())
            })
        } else {
            // We cannot push the buffer if we do not know its destination.
            // Instead of throwing an exception, provide a warning and process all other buffers.
            gst_warning!(
                CAT,
                obj: element,
                "Cannot push buffer tagged as {} because no corresponding pad was created. Please check that upstream 'video/rgbd' CAPS contain all streams that are attached to the main buffer.",
                tag_title
            );
            Ok(gst::FlowSuccess::Ok)
        }
    }

    /// Push a stream-start event on the given pad, so that downstream can expect data flow.
    /// This function makes sure that the pad sends only one stream-start event.
    /// # Arguments
    /// * `src_pad` - The pad to push the event on.
    /// * `stream_name` - A unique name of the stream to push the event for.
    /// * `stream_identifier` - A stream identifier that uniquely identifies the current stream.
    fn push_stream_start(
        src_pad: &mut DemuxPad,
        stream_name: &str,
        stream_identifier: &StreamIdentifier,
    ) {
        if src_pad.pushed_stream_start {
            gst_debug!(CAT, "Stream start event for stream {} was already pushed this streaming session, skipping", stream_name);
            return;
        }

        if src_pad
            .pad
            .push_event(stream_identifier.build_stream_start_event(stream_name))
        {
            src_pad.pushed_stream_start = true;
            gst_debug!(CAT, "Stream start event pushed for stream {}", stream_name);
        } else {
            gst_warning!(
                CAT,
                "Count not send stream start event for stream {}",
                stream_name
            );
        }
    }

    /// Push the "stream-start" event on all pads in `self.src_pads` that have not yet seen a
    /// "stream-start" event.
    /// # Arguments
    /// * `stream_identifier` - An instance of the [StreamIdentifier](struct.StreamIdentifier.html) struct that identifies the stream we're currently working with.
    /// # Remarks
    /// * Requires `self.src_pads` to be exclusively locked for writing. Please ensure that it is
    /// unlocked when calling this function.
    fn push_stream_start_on_all_pads(&self, stream_identifier: &StreamIdentifier) {
        gst_debug!(CAT, "Pushing stream start event for all streams");
        for (stream_name, mut src_pad) in self.src_pads.write().unwrap().iter_mut() {
            Self::push_stream_start(&mut src_pad, &stream_name, stream_identifier);
        }
    }

    /// Timestamps all auxiliary buffers with the timestamps found in the given `main_buffer`.
    /// # Arguments
    /// * `main_buffer` - A reference to the main `video/rgbd` buffer.
    fn timestamp_aux_buffers_from_main(main_buffer: &mut gst::BufferRef) {
        // Get timestamp of the main buffer
        let common_pts = main_buffer.get_pts();
        let common_dts = main_buffer.get_dts();
        let common_duration = main_buffer.get_duration();

        // Go through all auxiliary buffers
        for mut meta in main_buffer.iter_meta_mut::<BufferMeta>() {
            // Make the buffer mutable so that we can edit its timestamps
            let additional_buffer = meta.buffer_mut();

            // Distribute the timestamp of the main buffer to the auxiliary buffers
            additional_buffer.set_pts(common_pts);
            additional_buffer.set_dts(common_dts);
            additional_buffer.set_duration(common_duration);
        }
    }

    /// Create a new sink pad for rgbddemux and register event and chain funtions for it.
    /// # Arguments
    /// * `element` - The element that represents the `rgbddemux` in GStreamer.
    /// # Returns
    /// * A new sink pad.
    fn create_sink_pad(element: &gst::Element) -> gst::Pad {
        let templ = element
            .get_pad_template("sink")
            .expect("rgbdmux: Failed to get 'sink' pad template");

        gst::Pad::builder_with_template(&templ, Some("sink"))
            .event_function(|_, parent, event| {
                Self::catch_panic_pad_function(
                    parent,
                    || false,
                    |rgbd_demux, element| rgbd_demux.sink_event(element, event),
                )
            })
            .chain_function(|_, parent, buffer| {
                Self::catch_panic_pad_function(
                    parent,
                    || Err(gst::FlowError::Error),
                    |rgbd_demux, element| rgbd_demux.sink_chain(element, buffer),
                )
            })
            .build()
    }
}

impl ObjectImpl for RgbdDemux {
    glib_object_impl!();

    fn constructed(&self, obj: &glib::Object) {
        self.parent_constructed(obj);
        let element = obj
            .downcast_ref::<gst::Element>()
            .expect("rgbddemux: Cannot cast object as GstElement");

        // Create sink pad from the template that is registered with the class and set all sink pad functions
        let sink_pad = Self::create_sink_pad(element);

        // Add the sink pad to the element
        element
            .add_pad(&sink_pad)
            .expect("rgbddemux: Failed to add sink pad to the element");
    }

    fn set_property(&self, _obj: &glib::Object, id: usize, value: &glib::Value) {
        let mut settings = self.settings.write().unwrap();

        match PROPERTIES[id] {
            subclass::Property(prop @ "distribute-timestamps", ..) => {
                let distribute_timestamps =
                    get_property_and_debug(*CAT, value, prop, settings.distribute_timestamps);
                settings.distribute_timestamps = distribute_timestamps;
            }
            _ => unimplemented!("Property is not implemented"),
        };
    }

    fn get_property(&self, _obj: &glib::Object, id: usize) -> Result<glib::Value, ()> {
        let settings = self.settings.read().unwrap();

        match PROPERTIES[id] {
            subclass::Property("distribute-timestamps", ..) => {
                Ok(settings.distribute_timestamps.to_value())
            }
            _ => unimplemented!("Property is not implemented"),
        }
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
