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
use gst::subclass::prelude::*;
use gst_base::prelude::*;
use gst_base::subclass::prelude::*;
use gst_depth_meta::buffer::BufferMeta;
use gst_depth_meta::tags::TagsMeta;
use std::error::Error;
use std::fmt;
use std::fmt::{Display, Formatter};
use std::sync::Mutex;

#[derive(Debug, Clone)]
struct MuxingError(&'static str);
impl Error for MuxingError {}
impl Display for MuxingError {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "RGBD muxing error: {}", self.0)
    }
}

// A struct representation of the `rgbdmux` element
struct RgbdMux {
    cat: gst::DebugCategory,
    sink_pads: Mutex<Vec<String>>,
}

impl ObjectSubclass for RgbdMux {
    const NAME: &'static str = "rgbdmux";
    type ParentType = gst_base::Aggregator;
    type Instance = gst::subclass::ElementInstanceStruct<Self>;
    type Class = subclass::simple::ClassStruct<Self>;

    glib_object_subclass!();

    fn new() -> Self {
        Self {
            cat: gst::DebugCategory::new(
                "rgbdmux",
                gst::DebugColorFlags::empty(),
                Some("RGB-D Muxer"),
            ),
            sink_pads: Mutex::new(Vec::new()),
        }
    }

    fn class_init(klass: &mut subclass::simple::ClassStruct<Self>) {
        klass.set_metadata(
            "RGB-D Muxer",
            "Muxer/RGB-D",
            "Muxes multiple `video/x-raw` into a single `video/rgbd`",
            "Andrej Orsula <andrej.orsula@aivero.com>",
        );

        // sink pads
        let mut sink_caps = gst::Caps::new_simple("video/x-raw", &[]);
        sink_caps
            .get_mut()
            .expect("Could not get mutable reference to sink_caps")
            .append(gst::Caps::new_simple("meta/x-klv", &[("parsed", &true)]));
        klass.add_pad_template(
            gst::PadTemplate::new_with_gtype(
                "sink_%s",
                gst::PadDirection::Sink,
                gst::PadPresence::Request,
                &sink_caps,
                gst_base::AggregatorPad::static_type(),
            )
            .expect("Could not add sink-pad template to class"),
        );

        // src pad
        klass.add_pad_template(
            gst::PadTemplate::new_with_gtype(
                "src",
                gst::PadDirection::Src,
                gst::PadPresence::Always,
                &gst::Caps::new_simple("video/rgbd", &[]),
                gst_base::AggregatorPad::static_type(),
            )
            .expect("Could not add src-pad template to class"),
        );
    }
}

impl ObjectImpl for RgbdMux {
    glib_object_impl!();
}

impl ElementImpl for RgbdMux {
    fn release_pad(&self, element: &gst::Element, pad: &gst::Pad) {
        // De-activate the pad
        pad.set_active(false)
            .expect(&format!("Could not deactivate a sink-pad: {:?}", pad));

        // Remove the pad from the element
        element
            .remove_pad(pad)
            .expect(&format!("Could not remove a sink-pad: {:?}", pad));

        // Remove the pad from our internal reference HashMap
        let pad_name = pad.get_name().as_str().to_string();
        gst_debug!(self.cat, obj: element, "release_pad: {}", pad_name);
        self.sink_pads
            .lock()
            .expect("Could not lock sink_pads")
            .retain(|x| *x != pad_name);

        self.renegotiate_downstream_caps(element);
    }
}

impl AggregatorImpl for RgbdMux {
    fn aggregate(
        &self,
        aggregator: &gst_base::Aggregator,
        _timeout: bool,
    ) -> std::result::Result<gst::FlowSuccess, gst::FlowError> {
        // Get the list of available names
        let sink_pad_names = &self.sink_pads.lock().expect("Could not lock sink_pads");
        let mut sink_pad_names_iter = sink_pad_names.iter();

        // TODO (minor): Consider making `depth` stream always first/located in the main buffer if it is enabled

        // Put the first buffer in the list into the main buffer
        let first_sink_pad_name = sink_pad_names_iter
            .next()
            .ok_or(gst::FlowError::NotLinked)?;
        let mut main_output_buffer = self
            .get_tagged_buffer(aggregator, first_sink_pad_name)
            .map_err(|e| {
                gst_error!(self.cat, "{}", e);
                gst::FlowError::Error
            })?;

        // Attach the rest of the streams as meta to the main buffer
        for sink_pad_name in sink_pad_names_iter {
            // Extract and tag a buffer from the given sink pad
            let mut additional_output_buffer = self
                .get_tagged_buffer(aggregator, sink_pad_name)
                .map_err(|e| {
                    gst_error!(self.cat, "{}", e);
                    gst::FlowError::Error
                })?;

            // Attach the additional buffer to the main buffer
            BufferMeta::add(
                main_output_buffer
                    .get_mut()
                    .expect("Could not get mutable reference to main buffer"),
                &mut additional_output_buffer,
            );
        }
        self.finish_buffer(aggregator, main_output_buffer)
    }

    fn create_new_pad(
        &self,
        aggregator: &gst_base::Aggregator,
        _templ: &gst::PadTemplate,
        req_name: Option<&str>,
        _caps: Option<&gst::Caps>,
    ) -> Option<gst_base::AggregatorPad> {
        match req_name {
            // Make sure the name is valid
            None => {
                gst_error!(self.cat, obj: aggregator, "Invalid request pad name");
                return None;
            }
            Some(name) => {
                let mut sink_pads = self.sink_pads.lock().expect("Cannot lock sink_pads");
                gst_debug!(
                    self.cat,
                    obj: aggregator,
                    "create_new_pad for name: {}",
                    name
                );
                // Create new sink pad from the template
                let new_sink_pad = gst::Pad::new_from_template(
                    &aggregator
                        .get_pad_template("sink_%s")
                        .expect("Could not find sink-pad template"),
                    Some(name),
                )
                .downcast::<gst_base::AggregatorPad>()
                .expect("Could not cast pad to AggregatorPad");

                // Drop all buffers on already existing pads (if any)
                for pad_name in sink_pads.iter() {
                    loop {
                        if aggregator
                            .get_static_pad(pad_name)
                            .expect(
                                format!("Could not get static pad with name {}", pad_name).as_str(),
                            )
                            .downcast::<gst_base::AggregatorPad>()
                            .expect("Could not downcast pad to AggregatorPad")
                            .drop_buffer()
                            == false
                        {
                            break;
                        }
                    }
                }

                // Insert the new sink pad name into the struct
                sink_pads.push(name.to_string());

                // Activate the sink pad
                new_sink_pad
                    .set_active(true)
                    .expect("Failed to activate `rgbdmux` sink pad");

                Some(new_sink_pad)
            }
        }
    }

    fn update_src_caps(
        &self,
        aggregator: &gst_base::Aggregator,
        _caps: &gst::Caps,
    ) -> Result<gst::Caps, gst::FlowError> {
        gst_debug!(self.cat, "update_src_caps");
        let no_sink_pads = {
            self.sink_pads
                .lock()
                .expect("Could not lock sink pads")
                .len()
        };
        match no_sink_pads {
            0 => Err(gst_base::AGGREGATOR_FLOW_NEED_DATA), // https://gstreamer.freedesktop.org/documentation/base/gstaggregator.html?gi-language=c#GST_AGGREGATOR_FLOW_NEED_DATA
            _ => Ok(self.get_current_downstream_caps(aggregator.upcast_ref::<gst::Element>())),
        }
    }

    fn fixate_src_caps(&self, aggregator: &gst_base::Aggregator, _caps: gst::Caps) -> gst::Caps {
        let elm = aggregator.upcast_ref::<gst::Element>();
        gst_debug!(self.cat, obj: elm, "fixate_src_caps");
        {
            let sps = self.sink_pads.lock().expect("Could not lock sink_pads");
            gst_debug!(self.cat, obj: elm, "Streams: {}", sps.join(", "));
        }
        self.get_current_downstream_caps(elm)
    }
}

impl RgbdMux {
    /// Get a buffer from the pad with the given `pad_name` on the given `aggregator`. This function
    /// also tags the buffer with a correct title tag.
    /// # Arguments
    /// * `aggregator` - The aggregator that holds a pad with the given name.
    /// * `pad_name` - The name of the pad to read a buffer from.
    fn get_tagged_buffer(
        &self,
        aggregator: &gst_base::Aggregator,
        pad_name: &str,
    ) -> Result<gst::Buffer, MuxingError> {
        let mut buffer = aggregator
            .get_static_pad(pad_name)
            .expect(format!("Could not get static pad with name {}", pad_name).as_str())
            .downcast::<gst_base::AggregatorPad>()
            .expect("Could not downcast pad to AggregatorPad")
            .pop_buffer()
            .ok_or(MuxingError("No buffer available on static pad"))?;

        // Add tag title according to the main stream name (remove `sink_` from sink pad name)
        let mut tags = gst::tags::TagList::new();
        tags.get_mut()
            .ok_or(MuxingError("Could not get mutable reference to tags"))?
            .add::<gst::tags::Title>(&&pad_name[5..], gst::TagMergeMode::Append);
        let mut_buffer = buffer.make_mut();
        TagsMeta::add(mut_buffer, &mut tags);
        Ok(buffer)
    }

    /// Extracts the relevant fields from the pad's CAPS and converts them into a tuple containing
    /// the field's name as the first and its value as second.
    /// # Arguments
    /// * `pad_caps` - A reference to the pad's CAPS.
    /// * `pad_name` - The name of the stream we're currently generating CAPS for.
    fn push_sink_caps_format(
        &self,
        pad_caps: &gst::Caps,
        pad_name: &str,
        src_caps: &mut gst::StructureRef,
    ) {
        let pad_caps = pad_caps.iter().next().expect("Got empty CAPS in rgbdmux");
        let stream_name = &pad_name[5..];

        // Filter out all CAPS we don't care about and map those we do into strings
        for (field, value) in pad_caps.iter() {
            match field {
                "format" => {
                    let src_field_name = format!("{}_{}", stream_name, field);
                    src_caps.set(&src_field_name, &value.get::<&str>().unwrap());
                }
                "width" => {
                    let src_field_name = format!("{}_{}", stream_name, field);
                    src_caps.set(&src_field_name, &value.get::<i32>().unwrap());
                }
                "height" => {
                    let src_field_name = format!("{}_{}", stream_name, field);
                    src_caps.set(&src_field_name, &value.get::<i32>().unwrap());
                }
                _ => {
                    gst_info!(
                        self.cat,
                        "Ignored CAPS field {} of stream {}",
                        field,
                        stream_name,
                    );
                }
            }
        }
    }

    /// Get the current downstream CAPS. The downstream CAPS are generated based on the current sink
    /// pads on the muxer.
    /// # Arguments
    /// * `element` - The element that represents the `rgbdmux`.
    fn get_current_downstream_caps(&self, element: &gst::Element) -> gst::Caps {
        // First lock sink_pads, so that we may iterate it
        let sink_pads = self
            .sink_pads
            .lock()
            .expect("Failed to obtain `sink_pads` lock.");

        // Join all the pad names to create the 'streams' section of the CAPS
        let streams = sink_pads
            .iter()
            .map(|s| &s[5..])
            .collect::<Vec<&str>>()
            .join(",");

        // TODO: Remove hardcoded framerate
        let mut downstream_caps = gst::Caps::new_simple(
            "video/rgbd",
            &[
                ("streams", &streams),
                ("framerate", &gst::Fraction::new(30, 1)),
            ],
        );
        let mut_caps = downstream_caps
            .make_mut()
            .get_mut_structure(0)
            .expect("Could not get mutable CAPS in rgbdmux");

        // Map the caps into their corresponding stream formats
        for pad_name in sink_pads.iter() {
            // First find the current CAPS of Pad we're currently dealing with
            let pad_caps = element
                .get_static_pad(pad_name)
                .expect(&format!(
                    "Could not get static pad from aggregator with name `{}`",
                    pad_name
                ))
                .get_current_caps();
            match pad_caps {
                Some(pc) => self.push_sink_caps_format(&pc, pad_name, mut_caps),
                None => { /*ignore*/ }
            }
        }

        gst_info!(
            self.cat,
            obj: element,
            "stream_caps were found to be: {:?}.",
            downstream_caps
        );

        downstream_caps.to_owned()
    }

    /// Generates and sends new CAPS for the downstream elements. This function automatically
    /// generates CAPS based on the sink_pads of the muxer and their current CAPS.
    /// # Arguments
    /// * `element` - The element that represents the `rgbdmux`.
    fn renegotiate_downstream_caps(&self, element: &gst::Element) {
        gst_debug!(self.cat, obj: element, "renegotiate_downstream_caps");
        // Figure out the new caps the element should output
        let ds_caps = self.get_current_downstream_caps(element);
        // And send a CAPS event downstream
        let caps_event = gst::Event::new_caps(&ds_caps).build();
        if !element.send_event(caps_event) {
            gst_error!(
                self.cat,
                obj: element,
                "Failed to send CAPS negotiation event"
            );
        }
    }
}

pub fn register(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    gst::Element::register(
        Some(plugin),
        "rgbdmux",
        gst::Rank::None,
        RgbdMux::get_type(),
    )
}

mod tests {
    #[test]
    fn convert_depth_only_caps_to_rgbd() {
        gst::init().expect("Failed to gst::init() in convert_pad_caps_to_rgbd_caps");
        let rgbdmux = RgbdMux {
            cat: gst::DebugCategory::new(
                "rgbdmux_tests",
                gst::DebugColorFlags::FG_CYAN,
                Some("Unit tests for rgbdmux"),
            ),
            sink_pads: Mutex::new(vec![]),
        };
        let pad_caps = gst::Caps::new_simple(
            "video/x-raw",
            &[("format", &"GRAY8"), ("width", &1280), ("height", &720)],
        );

        let rgbd_caps = rgbdmux.get_caps_fields(&pad_caps, "depth");

        assert_eq!(
            rgbd_caps,
            "depth_format=GRAY8,depth_width=1280,depth_height=720"
        );
    }
}
