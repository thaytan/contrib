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
use gst_depth_meta::buffer::BufferMeta;
use gst_depth_meta::tags::TagsMeta;
use std::collections::HashMap;
use std::error::Error;
use std::fmt;
use std::fmt::{Display, Formatter};
use std::sync::Mutex;

#[derive(Debug, Clone)]
pub struct RgbdDemuxingError(pub String);
impl Error for RgbdDemuxingError {}
impl Display for RgbdDemuxingError {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "DddqEncError: {:?}", self.0)
    }
}
impl From<RgbdDemuxingError> for gst::FlowError {
    fn from(error: RgbdDemuxingError) -> Self {
        gst_error!(
            gst::DebugCategory::new(
                "dddqenc",
                gst::DebugColorFlags::empty(),
                Some("3DQ Encoder"),
            ),
            "{:?}",
            error
        );
        // TODO: Find out how to log the error here
        gst::FlowError::Error
    }
}

// A struct representation of the `rgbddemux` element
struct RgbdDemux {
    cat: gst::DebugCategory,
    internals: Mutex<RgbdDemuxInternals>,
}

// Internals of the element that are under Mutex
struct RgbdDemuxInternals {
    src_pads: HashMap<String, gst::Pad>,
    flow_combiner: gst_base::UniqueFlowCombiner,
}

impl RgbdDemux {
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
        gst_debug!(self.cat, obj: element, "sink_event");
        use gst::EventView;
        match event.view() {
            EventView::Caps(caps) => {
                gst_debug!(self.cat, obj: element, "Got a new caps event: {:?}", caps);
                // Call function that creates src pads according to the received Caps event
                match self.create_additional_src_pads(element, caps.get_caps()) {
                    Ok(_) => true,
                    Err(e) => {
                        gst_warning!(self.cat, obj: element, "{}", e);
                        false
                    }
                }
            }
            EventView::StreamStart(_id) => {
                // Accept any StreamStart event
                true
            }
            _ => {
                // By default, pass any other event to all src pads
                let src_pads = &self
                    .internals
                    .lock()
                    .expect("Could not lock internals")
                    .src_pads;
                if src_pads.len() == 0 {
                    // Return false if there is no src pad yet since this element does not handle it
                    return false;
                }

                let mut bool_flow_combiner = true;
                for src_pad in src_pads.values() {
                    // Forward the event to all src pads
                    // Set flow combiner to false if sending an event to any src pad fails
                    bool_flow_combiner = src_pad.send_event(event.clone());
                }
                bool_flow_combiner
            }
        }
    }

    /// Create additional src pads, which happens as a result of a CAPS renegotiation.
    /// # Arguments
    /// * `element` - The element that represents `rgbddemux` in GStreamer.
    /// * `rgbd_caps` - The CAPS that we should create src pads for.
    fn create_additional_src_pads(
        &self,
        element: &gst::Element,
        rgbd_caps: &gst::CapsRef,
    ) -> Result<(), RgbdDemuxingError> {
        // Extract the `video/rgbd` caps fields from gst::CapsRef
        let rgbd_caps = rgbd_caps.iter().next().ok_or(RgbdDemuxingError(
            "Invalid `video/rgbd` caps for creation of additional src pads".to_owned(),
        ))?;

        // Determine what streams are contained within the caps
        let streams = rgbd_caps
            .get::<&str>("streams")
            .ok_or(RgbdDemuxingError(
                "No `streams` field detected in `video/rgbd` caps".to_owned(),
            ))?
            .split(',')
            .collect::<Vec<&str>>();

        if streams.len() == 0 {
            return Err(RgbdDemuxingError(
                "Cannot detect any stream in `video/rgbd` caps under field `streams`".to_owned(),
            ));
        }

        // Get a common framerate for all streams
        let common_framerate =
            rgbd_caps
                .get::<gst::Fraction>("framerate")
                .ok_or(RgbdDemuxingError(
                    "Cannot detect any `framerate` in `video/rgbd` caps".to_owned(),
                ))?;

        // Iterate over all streams
        for stream_name in streams.iter() {
            // Extract `video/x-raw` caps from the `video/rgbd` caps for the particular stream
            let new_pad_caps =
                self.extract_stream_caps(stream_name, &rgbd_caps, &common_framerate)?;

            // Create the new src pad with given caps and stream name
            self.create_new_src_pad(element, new_pad_caps, stream_name);
        }
        Ok(())
    }

    /// Extract CAPS for the given stream from the given rgbd_caps.
    /// # Arguments
    /// * `stream_name` - The name of the stream to extract CAPS for, e.g. `depth`.
    /// * `rgbd_caps` - A referece to the `video/rgbd` CAPS, from which the stream's CAPS should be extracted.
    /// * `common_framerate` - The framerate of all the streams.
    fn extract_stream_caps(
        &self,
        stream_name: &str,
        rgbd_caps: &gst::StructureRef,
        common_framerate: &gst::Fraction,
    ) -> Result<gst::Caps, RgbdDemuxingError> {
        // Get the format of a stream
        let stream_format = rgbd_caps
            .get::<&str>(&format!("{}_format", stream_name))
            .ok_or(RgbdDemuxingError(
                "Cannot detect any `format` in `video/rgbd` caps for `{}` stream".to_owned(),
            ))?;

        // Get the width of a stream
        let stream_width = rgbd_caps
            .get::<i32>(&format!("{}_width", stream_name))
            .ok_or(RgbdDemuxingError(
                "Cannot detect any `width` in `video/rgbd` caps for `{}` stream".to_owned(),
            ))?;

        // Get the height of a stream
        let stream_height = rgbd_caps
            .get::<i32>(&format!("{}_height", stream_name))
            .ok_or(RgbdDemuxingError(
                "Cannot detect any `height` in `video/rgbd` caps for `{}` stream".to_owned(),
            ))?;

        // Create caps for the new src pad
        Ok(gst::Caps::new_simple(
            "video/x-raw",
            &[
                ("format", &stream_format),
                ("width", &stream_width),
                ("height", &stream_height),
                ("framerate", common_framerate),
            ],
        ))
    }

    /// Create a new src pad on the `rgbddemux` for the stream with the given name.
    /// # Arguments
    /// * `element` - The element that represents the `rgbddemux` in GStreamer.
    /// * `new_pad_caps` - The CAPS that should be used on the new src pad.
    /// * `stream_name` - The name of the stream to create a src pad for.
    fn create_new_src_pad(
        &self,
        element: &gst::Element,
        new_pad_caps: gst::Caps,
        stream_name: &str,
    ) {
        // Lock the internals
        let internals = &mut *self.internals.lock().expect("Could not lock internals");

        // Create naming for the src pad according to the stream
        let new_src_pad_name = &format!("src_{}", stream_name);

        // In case such pad already exists (during re-negotiation), release the existing pad
        if internals.src_pads.get(&new_src_pad_name.to_string()).is_some() {
            gst_info!(
                self.cat,
                obj: element,
                "Pad `{}` already exists. Releasing...",
                new_src_pad_name
            );
            self.release_src_pad(element, new_src_pad_name, internals);
        }

        // Create the src pad with these caps
        let new_src_pad = gst::Pad::new_from_template(
            &element
                .get_pad_template("sink")
                .expect("No sink pad template registered in rgbddemux"),
            Some(new_src_pad_name),
        );

        // Add the src pad to the element and activate it
        element
            .add_pad(&new_src_pad)
            .expect("Could not add src pad template in rgbddemux");
        new_src_pad
            .set_active(true)
            .expect("Could not activate new src pad in rgbddemux");

        // Push events on this src pad. It is assumed here that the pad is already linked and the downstream element accepts the caps.
        new_src_pad.send_event(
            gst::event::Event::new_stream_start(stream_name)
                .group_id(gst::util_group_id_next())
                .build(),
        );
        new_src_pad.send_event(gst::event::Event::new_caps(&new_pad_caps).build());

        // Add the new pad to the internals
        internals.flow_combiner.add_pad(&new_src_pad);
        internals
            .src_pads
            .insert(new_src_pad_name.to_string(), new_src_pad);
    }

    /// Release a src pad from the `rgbddemux`, dropping all its buffers and removing it from the element.
    /// # Arguments
    /// * `element` - The element that represents the `rgbddemux` in GStreamer.
    /// * `src_pad_name` - The name of the src pad to release.
    /// * `internals` - A locked reference to the `rgbddemux`'s internal state.
    fn release_src_pad(&self, element: &gst::Element, src_pad_name: &str, internals: &mut RgbdDemuxInternals) {
        // Get reference to the pad with given name
        let src_pad = &internals.src_pads.get(src_pad_name).expect(&format!(
            "No src pad with name `{}` in rgbddemux",
            src_pad_name
        ));

        // Deactivate this pad
        src_pad.set_active(false).expect(&format!(
            "Failed to deactivate src pad `{}` in rgbddemux",
            src_pad_name
        ));
        // Remove pad from the element
        element.remove_pad(*src_pad).expect(&format!(
            "Failed to remove src pad `{}` in rgbddemux",
            src_pad_name
        ));

        // Remove pad from the internals
        internals.flow_combiner.remove_pad(*src_pad);
        internals
            .src_pads
            .remove(&src_pad_name.to_string())
            .expect(&format!(
                "Failed to remove src pad `{}` from internal map in rgbddemux",
                src_pad_name
            ));
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
        let internals = &mut *self
            .internals
            .lock()
            .expect("Failed to lock internals in rgbddemux");

        // Go through all meta buffers attached to the main buffer in order to extract them and push to the corresponding src pads
        for meta in main_buffer.iter_meta::<BufferMeta>() {
            // Get GstBuffer from meta of the main buffer
            let additional_buffer = unsafe { gst::buffer::Buffer::from_glib_none(meta.buffer) };

            // Push the additional buffer to the corresponding src pad
            let _flow_combiner_result =
                internals
                    .flow_combiner
                    .update_flow(self.push_buffer_to_corresponding_pad(
                        &internals.src_pads,
                        additional_buffer,
                    ).map_err(|e| {
                        gst_error!(
                            self.cat,
                            obj: element,
                            "{}", e
                        );
                        gst::FlowError::Error
                    }));
        }

        // Push the main buffer to the corresponding src pad
        internals
            .flow_combiner
            .update_flow(self.push_buffer_to_corresponding_pad(
                &internals.src_pads,
                main_buffer,
            ).map_err(|e| {
                gst_error!(
                            self.cat,
                            obj: element,
                            "{}", e
                        );
                gst::FlowError::Error
            }))
    }

    /// Push the given buffer to the src pad that was allocated for it.
    /// # Arguments
    /// * `element` - The element that represents the `rgbddemux` in GStreamer.
    /// * `src_pads` - A hash map that associates buffer title tags with their corresponding pad.
    /// * `buffer` - The buffer that should be pushed further downstream.
    fn push_buffer_to_corresponding_pad(
        &self,
        src_pads: &HashMap<String, gst::Pad>,
        buffer: gst::Buffer,
    ) -> Result<gst::FlowSuccess, RgbdDemuxingError> {
        // Extract tag title from the buffer
        let tag_title = self.extract_tag_title(&buffer)?;

        // Match the tag title with a corresponding src pad
        let src_pad = src_pads.get(&(format!("src_{}", tag_title))).ok_or(RgbdDemuxingError(format!("No corresponding pad for buffer with tag title `{}` exists", tag_title)))?;
        src_pad.push(buffer).map_err(|_| RgbdDemuxingError("Failed to push buffer onto its corresponding pad".to_owned()))
    }

    /// Extract the Title tag from the given buffer.
    /// # Arguments
    /// * `buffer` - The buffer from which the title tag should be extracted.
    fn extract_tag_title(&self, buffer: &gst::Buffer) -> Result<String, RgbdDemuxingError> {
        // Get GstTagList from GstBuffer
        let meta = buffer.get_meta::<TagsMeta>().ok_or(RgbdDemuxingError(format!("No meta detected in buffer `{:?}`", buffer)))?;
        let tag_list = unsafe { gst::tags::TagList::from_glib_none(meta.tags) };

        // Get the tag title from GstTagList
        let gst_tag_title = &tag_list.get::<gst::tags::Title>().ok_or(RgbdDemuxingError(format!("No tag title detected in buffer `{:?}`", buffer)))?;
        let title = gst_tag_title.get().ok_or(RgbdDemuxingError(format!("Invalid tag title detected in buffer `{:?}`", buffer)))?;
        Ok(title.to_string())
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
            cat: gst::DebugCategory::new(
                "rgbddemux",
                gst::DebugColorFlags::empty(),
                Some("RGB-D Demuxer"),
            ),
            internals: Mutex::new(RgbdDemuxInternals {
                src_pads: HashMap::new(),
                flow_combiner: gst_base::UniqueFlowCombiner::new(),
            }),
        }
    }

    fn class_init(klass: &mut subclass::simple::ClassStruct<Self>) {
        klass.set_metadata(
            "RGB-D Demuxer",
            "Demuxer/RGB-D",
            "Demuxes  a single `video/rgbd` into multiple `video/x-raw`",
            "Raphael Dürscheid <rd@aivero.com>, Andrej Orsula <andrej.orsula@aivero.com>",
        );

        // src pads
        klass.add_pad_template(
            gst::PadTemplate::new(
                "src_%s",
                gst::PadDirection::Src,
                gst::PadPresence::Sometimes,
                &gst::Caps::new_simple("video/x-raw", &[]),
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
}

impl ElementImpl for RgbdDemux {}

pub fn register(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    gst::Element::register(
        Some(plugin),
        "rgbddemux",
        gst::Rank::None,
        RgbdDemux::get_type(),
    )
}
