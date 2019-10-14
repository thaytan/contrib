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
        self.sink_pads
            .lock()
            .expect("Could not lock sink_pads")
            .retain(|x| *x != pad_name);
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
                for pad_name in self
                    .sink_pads
                    .lock()
                    .expect("Could nok lock sink_pads")
                    .iter()
                {
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

                // TODO (important): fix downstream re-negotiation

                // Insert the new sink pad name into the struct
                self.sink_pads
                    .lock()
                    .expect("Could not lock sink_pads")
                    .push(name.to_string());

                // Activate the sink pad
                new_sink_pad
                    .set_active(true)
                    .expect("Failed to activate `rgbdmux` sink pad");

                Some(new_sink_pad)
            }
        }
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
        TagsMeta::add(buffer.make_mut(), &mut tags);
        Ok(buffer)
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
