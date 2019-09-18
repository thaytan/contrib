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
use std::sync::Mutex;

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
    // Each function is wrapped in catch_panic_pad_function(), which will
    // - Catch panics from the pad functions and instead of aborting the process
    //   it will simply convert them into an error message and poison the element
    //   instance
    // - Extract RgbdDemux struct from the object instance and pass it to us
    fn set_sink_pad_functions(sink_pad: &gst::Pad) {
        // Sink Event
        sink_pad.set_event_function(|pad, parent, event| {
            RgbdDemux::catch_panic_pad_function(
                parent,
                || false,
                |rgbd_demux, element| rgbd_demux.sink_event(pad, element, event),
            )
        });
        // Sink Chain
        sink_pad.set_chain_function(|pad, parent, buffer| {
            RgbdDemux::catch_panic_pad_function(
                parent,
                || Err(gst::FlowError::Error),
                |rgbd_demux, element| rgbd_demux.sink_chain(pad, element, buffer),
            )
        });
    }

    // Called whenever an event is received at the sink pad
    fn sink_event(&self, _pad: &gst::Pad, element: &gst::Element, event: gst::Event) -> bool {
        use gst::EventView;
        match event.view() {
            EventView::Caps(caps) => {
                // Call function that creates src pads according to the received Caps event
                self.create_additional_src_pads(element, caps.get_caps())
            }
            EventView::StreamStart(_id) => {
                // Accept any StreamStart event
                true
            }
            _ => {
                // By default, pass any other event to all src pads
                let src_pads = &self.internals.lock().unwrap().src_pads;
                if src_pads.len() == 0 {
                    // Return false if there is no src pad yet since this element does not handle it
                    return false;
                }

                let mut bool_flow_combiner = true;
                for src_pad in src_pads.values() {
                    // Push the event to all src pads
                    if !src_pad.push_event(event.clone()) {
                        // Set flow combiner to false if pushing an event to any src pad fails
                        bool_flow_combiner = false;
                    }
                }
                bool_flow_combiner
            }
        }
    }

    fn create_additional_src_pads(&self, element: &gst::Element, rgbd_caps: &gst::CapsRef) -> bool {
        // Extract the `video/rgbd` caps fields from gst::CapsRef
        let rgbd_caps = if let Some(caps) = rgbd_caps.iter().next() {
            caps
        } else {
            gst_error!(
                self.cat,
                obj: element,
                "Invalid `video/rgbd` caps for creation of additional src pads"
            );
            return false;
        };

        // Determine what streams are contained within the caps
        let streams: Vec<&str> = if let Some(streams) = rgbd_caps.get::<&str>("streams") {
            streams.split(',').collect()
        } else {
            gst_error!(
                self.cat,
                obj: element,
                "No `streams` field detected in `video/rgbd` caps"
            );
            return false;
        };
        if streams.len() == 0 {
            gst_error!(
                self.cat,
                obj: element,
                "Cannot detect any stream in `video/rgbd` caps under field `streams`"
            );
            return false;
        }

        // Get a common framerate for all streams
        let common_framerate = if let Some(framerate) = rgbd_caps.get::<gst::Fraction>("framerate")
        {
            framerate
        } else {
            gst_error!(
                self.cat,
                obj: element,
                "Cannot detect any `framerate` in `video/rgbd` caps"
            );
            return false;
        };

        // Iterate over all streams
        for stream_name in streams.iter() {
            // Determine the appropriate caps for the stream
            let new_pad_caps = if *stream_name == "meta" {
                // Get `video/meta-klv` caps if the `meta` stream is enabled
                gst::Caps::new_simple("meta/x-klv", &[("parsed", &true)])
            } else {
                // Extract `video/x-raw` caps from the `video/rgbd` caps for the particular stream
                if let Some(new_caps) =
                    self.extract_stream_caps(element, stream_name, &rgbd_caps, &common_framerate)
                {
                    new_caps
                } else {
                    return false;
                }
            };

            // Create the new src pad with given caps and stream name
            self.create_new_src_pad(element, new_pad_caps, stream_name);
        }
        true
    }

    fn extract_stream_caps(
        &self,
        element: &gst::Element,
        stream_name: &str,
        rgbd_caps: &gst::StructureRef,
        common_framerate: &gst::Fraction,
    ) -> Option<gst::Caps> {
        // Get the format of a stream
        let stream_format =
            if let Some(format) = rgbd_caps.get::<&str>(&format!("{}_format", stream_name)) {
                format
            } else {
                gst_error!(
                    self.cat,
                    obj: element,
                    "Cannot detect any `format` in `video/rgbd` caps for `{}` stream",
                    stream_name
                );
                return None;
            };
        // Get the width of a stream
        let stream_width =
            if let Some(width) = rgbd_caps.get::<i32>(&format!("{}_width", stream_name)) {
                width
            } else {
                gst_error!(
                    self.cat,
                    obj: element,
                    "Cannot detect any `width` in `video/rgbd` caps for `{}` stream",
                    stream_name
                );
                return None;
            };
        // Get the height of a stream
        let stream_height =
            if let Some(height) = rgbd_caps.get::<i32>(&format!("{}_height", stream_name)) {
                height
            } else {
                gst_error!(
                    self.cat,
                    obj: element,
                    "Cannot detect any `height` in `video/rgbd` caps for `{}` stream",
                    stream_name
                );
                return None;
            };

        // Create caps for the new src pad
        Some(gst::Caps::new_simple(
            "video/x-raw",
            &[
                ("format", &stream_format),
                ("width", &stream_width),
                ("height", &stream_height),
                ("framerate", common_framerate),
            ],
        ))
    }

    fn create_new_src_pad(
        &self,
        element: &gst::Element,
        new_pad_caps: gst::Caps,
        stream_name: &str,
    ) {
        // Lock the internals
        let internals = &mut *self.internals.lock().unwrap();

        // Create naming for the src pad according to the stream
        let new_src_pad_name = &format!("src_{}", stream_name);

        // In case such pad already exists (during re-negotiation), release the existing pad
        if let Some(_already_existing_pad) = internals.src_pads.get(&new_src_pad_name.to_string()) {
            gst_info!(
                self.cat,
                obj: element,
                "Pad `{}` already exists. Releasing...",
                new_src_pad_name
            );
            self.release_src_pad(element, new_src_pad_name);
        }

        // Create the src pad with these caps
        let new_src_pad = gst::Pad::new_from_template(
            &gst::PadTemplate::new(
                new_src_pad_name,
                gst::PadDirection::Src,
                gst::PadPresence::Sometimes,
                &new_pad_caps,
            )
            .unwrap(),
            Some(new_src_pad_name),
        );

        // Add the src pad to the element and activate it
        element.add_pad(&new_src_pad).unwrap();
        new_src_pad.set_active(true).unwrap();

        // Push events on this src pad. It is assumed here that the pad is already linked and the downstream element accepts the caps.
        new_src_pad.push_event(
            gst::event::Event::new_stream_start(stream_name)
                .group_id(gst::util_group_id_next())
                .build(),
        );
        new_src_pad.push_event(gst::event::Event::new_caps(&new_pad_caps).build());

        // Add the new pad to the internals
        internals.flow_combiner.add_pad(&new_src_pad);
        internals
            .src_pads
            .insert(new_src_pad_name.to_string(), new_src_pad);
    }

    fn release_src_pad(&self, element: &gst::Element, src_pad_name: &str) {
        // Lock the internals
        let internals = &mut *self.internals.lock().unwrap();
        // Get reference to the pad with given name
        let src_pad = &internals.src_pads.get(src_pad_name).unwrap();

        // Deactivate this pad
        src_pad.set_active(false).unwrap();
        // Remove pad from the element
        element.remove_pad(*src_pad).unwrap();

        // Remove pad from the internals
        internals.flow_combiner.remove_pad(*src_pad);
        internals
            .src_pads
            .remove(&src_pad_name.to_string())
            .unwrap();
    }

    // Called whenever a new buffer is passed to the sink pad
    fn sink_chain(
        &self,
        _pad: &gst::Pad,
        element: &gst::Element,
        main_buffer: gst::Buffer,
    ) -> Result<gst::FlowSuccess, gst::FlowError> {
        // Lock the internals
        let internals = &mut *self.internals.lock().unwrap();

        // Go through all meta buffers attached to the main buffer in order to extract them and push to the corresponding src pads
        for meta in main_buffer.iter_meta::<BufferMeta>() {
            // Get GstBuffer from meta of the main buffer
            let additional_buffer = unsafe { gst::buffer::Buffer::from_glib_none(meta.buffer) };

            // Push the additional buffer to the corresponding src pad
            let _flow_combiner_result =
                internals
                    .flow_combiner
                    .update_flow(self.push_buffer_to_corresponding_pad(
                        element,
                        &internals.src_pads,
                        additional_buffer,
                    ));
        }

        // Push the main buffer to the corresponding src pad
        internals
            .flow_combiner
            .update_flow(self.push_buffer_to_corresponding_pad(
                element,
                &internals.src_pads,
                main_buffer,
            ))
    }

    fn push_buffer_to_corresponding_pad(
        &self,
        element: &gst::Element,
        src_pads: &HashMap<String, gst::Pad>,
        buffer: gst::Buffer,
    ) -> Result<gst::FlowSuccess, gst::FlowError> {
        // Extract tag title from the buffer
        let tag_title = if let Some(tag_title) = self.extract_tag_title(element, &buffer) {
            tag_title
        } else {
            return Err(gst::FlowError::Error);
        };

        // Match the tag title with a corresponding src pad
        match src_pads.get(&(format!("src_{}", tag_title))) {
            Some(corresponding_pad) => {
                // Push the buffer to the corresponding pad
                return corresponding_pad.push(buffer);
            }
            None => {
                gst_warning!(
                    self.cat,
                    obj: element,
                    "No corresponding pad for buffer with tag title `{}` exists",
                    tag_title
                );
                return Err(gst::FlowError::Error);
            }
        }
    }

    fn extract_tag_title(&self, element: &gst::Element, buffer: &gst::Buffer) -> Option<String> {
        // Get GstTagList from GstBuffer
        let tag_list = match buffer.get_meta::<TagsMeta>() {
            Some(meta) => unsafe { gst::tags::TagList::from_glib_none(meta.tags) },
            None => {
                gst_error!(
                    self.cat,
                    obj: element,
                    "No meta detected in buffer `{:?}`",
                    buffer
                );
                return None;
            }
        };

        // Get the tag title from GstTagList
        let gst_tag_title = &tag_list.get::<gst::tags::Title>();
        // Convert GstTitle to &str
        match gst_tag_title {
            Some(tag_title) => {
                // Make sure the title is valid
                match tag_title.get() {
                    Some(title) => return Some(title.to_string()),
                    None => {
                        gst_error!(
                            self.cat,
                            obj: element,
                            "Invalid tag title detected in buffer `{:?}`",
                            buffer
                        );
                        return None;
                    }
                }
            }
            None => {
                gst_error!(
                    self.cat,
                    obj: element,
                    "No tag title detected in buffer `{:?}`",
                    buffer
                );
                return None;
            }
        }
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
        let mut src_caps = gst::Caps::new_simple("video/x-raw", &[]);
        src_caps
            .get_mut()
            .unwrap()
            .append(gst::Caps::new_simple("meta/x-klv", &[("parsed", &true)]));
        klass.add_pad_template(
            gst::PadTemplate::new(
                "src_%s",
                gst::PadDirection::Src,
                gst::PadPresence::Sometimes,
                &src_caps,
            )
            .unwrap(),
        );

        // sink pad
        klass.add_pad_template(
            gst::PadTemplate::new(
                "sink",
                gst::PadDirection::Sink,
                gst::PadPresence::Always,
                &gst::Caps::new_simple("video/rgbd", &[]),
            )
            .unwrap(),
        );
    }
}

impl ObjectImpl for RgbdDemux {
    glib_object_impl!();

    fn constructed(&self, obj: &glib::Object) {
        self.parent_constructed(obj);
        let element = obj.downcast_ref::<gst::Element>().unwrap();

        // Create sink pad from the template that is registered with the class
        let templ = element.get_pad_template("sink").unwrap();
        let sink_pad = gst::Pad::new_from_template(&templ, Some("sink"));

        // Set all sink pad functions
        Self::set_sink_pad_functions(&sink_pad);

        // Add the sink pad to the element
        element.add_pad(&sink_pad).unwrap();
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
