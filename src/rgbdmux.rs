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

const FRAME_DURATION: u64 = 250;
// TODO: make this duration

const DROP_ALL_BUFFERS_IF_ONE_IS_MISSING: bool = true;

// A struct representation of the `rgbdmux` element
struct RgbdMux {
    cat: gst::DebugCategory,
    sink_pads: Mutex<Vec<String>>,
    previous_timestamp: Mutex<gst::ClockTime>,
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
            previous_timestamp: Mutex::new(gst::CLOCK_TIME_NONE),
        }
    }

    fn class_init(klass: &mut subclass::simple::ClassStruct<Self>) {
        klass.set_metadata(
            "RGB-D Muxer",
            "Muxer/RGB-D",
            "Muxes multiple `video/x-raw` into a single `video/rgbd`",
            "Andrej Orsula <andrej.orsula@aivero.com>, Tobias Morell <tobias.morell@aivero.com>",
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
    /// This function provides a custom implementation to what should happen when request pads are
    /// released.
    /// # Arguments
    /// * `element` - The element that represents `rgbdmux` in GStreamer.
    /// * `pad` - The pad that is soon to be released.
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

        // TODO: We should check whether we're in the process of shutting down before calling this
        self.renegotiate_downstream_caps(element);
    }
}

impl AggregatorImpl for RgbdMux {
    fn aggregate(
        &self,
        aggregator: &gst_base::Aggregator,
        _timeout: bool,
    ) -> Result<gst::FlowSuccess, gst::FlowError> {
        // Get the list of available names
        let sink_pad_names = &self.sink_pads.lock().expect("Could not lock sink_pads");

        // TODO: determine whether it is necessary to make all the buffers drop if one is missing
        // TODO: otherwise, let `check_synchronisation()` deal with it

        // TODO: send gap event downstream if there is a discontinuity expected

        // Check all sink pads for queued buffers. If one pad has no queued buffer, drop all other buffers.
        let res = self.drop_buffers_if_one_missing(aggregator, sink_pad_names);
        if res.is_err() {
            // If all buffers were dropped, return CustomError
            println!("`drop_buffers_if_one_missing()` finished!");
            return Err(gst::FlowError::CustomError);
        }

        // Make sure the streams are synchronised
        if self
            .check_synchronisation(aggregator, sink_pad_names)
            .is_err()
        {
            // If buffers lacking behind were dropped, return CustomError1
            println!("`check_synchronisation()` finished!");
            return Err(gst::FlowError::CustomError1);
        }

        // Mux all buffers to a single output buffer.
        let output_buffer = self.mux_buffers(aggregator, sink_pad_names);
        if output_buffer.is_err() {
            // If muxing is not successful, do ... TODO: finish comment
            // TODO: currently `mux_buffers()` never returns an error
        }

        // Finish the buffer if all went fine
        self.finish_buffer(aggregator, output_buffer.unwrap())
    }

    /// This function is called when a peer element requests a pad. It provides a custom implementation
    /// for how the pad should be created.
    /// # Arguments
    /// * `aggregator` - The element that represents the `rgbdmux` in GStreamer.
    /// * `_templ` - (not used) The template that should be used in pad creation.
    /// * `req_name` - The requested name for the pad.
    /// * `_caps` - (not used) The CAPS to use for the pad.
    fn create_new_pad(
        &self,
        aggregator: &gst_base::Aggregator,
        _templ: &gst::PadTemplate,
        req_name: Option<&str>,
        _caps: Option<&gst::Caps>,
    ) -> Option<gst_base::AggregatorPad> {
        match req_name {
            Some(name) if name.starts_with("sink_") => {
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
            _ => {
                gst_error!(
                    self.cat,
                    obj: aggregator,
                    "Invalid request pad name. Only sink pads may be requested."
                );
                return None;
            }
        }
    }

    /// This function is called during CAPS negotiation. It can be used to decide on a CAPS format
    /// or delay the negotiation until sufficient data is present to decide on the CAPS (in this
    /// case when an upstream element has requested sink pads)
    /// # Arguments
    /// * `aggregator` - A reference to the element that represents `rgbdmux` in GStreamer.
    ///* `_caps` - (not used) The CAPS that is currently negotiated for the element.
    fn update_src_caps(
        &self,
        aggregator: &gst_base::Aggregator,
        _caps: &gst::Caps,
    ) -> Result<gst::Caps, gst::FlowError> {
        gst_debug!(self.cat, "update_src_caps");
        // Check how many sink pads has been created
        let no_sink_pads = {
            self.sink_pads
                .lock()
                .expect("Could not lock sink pads")
                .len()
        };
        // if no sink pads are present, we're not ready to negotiate CAPS, otherwise do the negotiation
        match no_sink_pads {
            0 => Err(gst_base::AGGREGATOR_FLOW_NEED_DATA), // we're not ready to decide on CAPS yet
            _ => Ok(self.get_current_downstream_caps(aggregator.upcast_ref::<gst::Element>())),
        }
    }

    /// This function is used to hint the type of CAPS we're expecting in the element.
    /// Right now the function simply ignores the suggested CAPS and pushes the one generated from
    /// the video/rgbd CAPS.
    /// # Arguments
    /// * `aggregator` - A reference to the element that represents `rgbdmux` in GStreamer.
    ///* `_caps` - (not used) The CAPS that is currently negotiated for the element.
    fn fixate_src_caps(&self, aggregator: &gst_base::Aggregator, _caps: gst::Caps) -> gst::Caps {
        let elm = aggregator.upcast_ref::<gst::Element>();
        gst_debug!(self.cat, obj: elm, "fixate_src_caps");
        self.get_current_downstream_caps(elm)
    }

    /// Called when the element needs to know the running time of the next rendered buffer for live pipelines.
    /// This causes deadline based aggregation to occur. Returning GST_CLOCK_TIME_NONE causes the element to
    /// wait for buffers on all sink pads before aggregating.
    /// # Arguments
    /// * `aggregator` - A reference to the element that represents `rgbdmux` in GStreamer.
    fn get_next_time(&self, _aggregator: &gst_base::Aggregator) -> gst::ClockTime {
        println!(
            "`get_next_time()`: {:#?}",
            *self.previous_timestamp.lock().unwrap() + gst::ClockTime::from_mseconds(FRAME_DURATION)
        );
        *self.previous_timestamp.lock().unwrap() + gst::ClockTime::from_mseconds(FRAME_DURATION)
    }
}

impl RgbdMux {
    /// Check whether the streams are synchronised based on their pts timestamps.
    /// If the streams are not synchronised, buffers that are bedind get dropped and error is returned.
    /// # Arguments
    /// * `aggregator` - The aggregator to consider.
    /// * `sink_pad_names` - The vector containing all sink pad names.
    /// # Returns
    /// * `Err(MuxingError)` - if frames
    #[inline]
    fn check_synchronisation(
        &self,
        aggregator: &gst_base::Aggregator,
        sink_pad_names: &Vec<String>,
    ) -> Result<(), MuxingError> {
        // Create a vector for storing timestamps of all buffers
        let mut timestamps: Vec<(&String, gst::ClockTime)> =
            Vec::with_capacity(sink_pad_names.len());

        // Iterate over all sink pads
        for sink_pad_name in sink_pad_names.iter() {
            // Get the sink pad given its name
            let sink_pad = Self::get_aggregator_pad(aggregator, sink_pad_name);

            // Extract a buffer from the given sink pad
            let buffer = sink_pad.peek_buffer();

            // Skip to the next pad if there is no buffer queued
            if buffer.is_none() {
                continue;
            }
            let buffer = buffer.unwrap();

            // Push the timestamp with the corresponing pad name
            timestamps.push((sink_pad_name, buffer.as_ref().get_pts()));
        }

        println!("timestamps: {:#?}", timestamps);

        // Find miximum and maximum timestamp
        let min = timestamps
            .iter()
            .min()
            .ok_or(MuxingError("No buffer was received"))?;
        let max = timestamps
            .iter()
            .max()
            .ok_or(MuxingError("No buffer was received"))?;

        // Update the current timestamp
        *self.previous_timestamp.lock().unwrap() = max.1;

        // If min and max timestamps are equal, the streams are synchronised
        if min.1 == max.1 {
            return Ok(());
        }

        // If the streams are not synchronised, drop frames that are behind
        gst_info!(
            self.cat,
            obj: aggregator,
            "Dropped buffers to synchronise the streams"
        );

        // Iterate over timestamps and drop all buffers that have timestamp
        // equal to the min timestamp (those that are behind)
        for timestamp in timestamps.iter() {
            if min.1 == timestamp.1 {
                // Get sink pad with the given name
                let sink_pad = Self::get_aggregator_pad(aggregator, timestamp.0);
                // Drop the buffer
                sink_pad.drop_buffer();
            }
        }

        // Return error
        Err(MuxingError("Dropped buffers to synchronise the streams"))
    }

    /// Mux all buffers to a single output buffer. All buffers are properly tagget with a title.
    /// # Arguments
    /// * `aggregator` - The aggregator to consider.
    /// * `sink_pad_names` - The vector containing all sink pad names.
    #[inline]
    fn mux_buffers(
        &self,
        aggregator: &gst_base::Aggregator,
        sink_pad_names: &Vec<String>,
    ) -> Result<gst::Buffer, MuxingError> {
        // Place a buffer from the first pad into the main buffer
        // If there is no buffer, leave the main buffer empty
        let mut main_buffer = Self::get_tagged_buffer(aggregator, &sink_pad_names[0])
            .unwrap_or_else(|_e| {
                gst_info!(
                    self.cat,
                    obj: aggregator,
                    "No buffer is queued on main `{}` pad. Leaving the buffer empty.",
                    sink_pad_names[0]
                );
                gst::Buffer::new()
            });

        // Get a mutable reference to the main buffer
        let main_buffer_mut_ref = main_buffer
            .get_mut()
            .expect("Could not get mutable reference to main buffer");

        // Iterate over all other sink pads, excluding the first one
        for sink_pad_name in sink_pad_names.iter().skip(1) {
            // Get a buffer that was queue on the sink pad and tag it with a title
            let buffer = Self::get_tagged_buffer(aggregator, sink_pad_name);

            // Check whether a buffer was received, otherwise skip
            if buffer.is_err() {
                gst_info!(
                    self.cat,
                    obj: aggregator,
                    "No buffer is queued on `{}` pad. Skipping.",
                    sink_pad_name
                );
                continue;
            }
            let mut buffer = buffer.unwrap();

            // Attach to the main bufer
            BufferMeta::add(main_buffer_mut_ref, &mut buffer);
        }
        // Return the main buffer
        Ok(main_buffer)
    }

    /// Get a buffer from the pad with the given `pad_name` on the given `aggregator`. This function
    /// also tags the buffer with a correct title tag.
    /// # Arguments
    /// * `aggregator` - The aggregator that holds a pad with the given name.
    /// * `pad_name` - The name of the pad to read a buffer from.
    #[inline]
    fn get_tagged_buffer(
        aggregator: &gst_base::Aggregator,
        pad_name: &str,
    ) -> Result<gst::Buffer, MuxingError> {
        // Get the sink pad given its name
        let sink_pad = Self::get_aggregator_pad(aggregator, pad_name);

        // Extract a buffer from the given sink pad
        let mut buffer = sink_pad
            .pop_buffer()
            .ok_or(MuxingError("No buffer queued on one of the pads"))?;

        // Get a mutable reference to the buffer
        let buffer_mut = buffer.get_mut().expect(&format!(
            "Could not get a mutable reference to buffer on `{}` pad",
            pad_name
        ));
        // Get the stream name by truncating the "sink_" prefix
        let stream_name = &pad_name[5..];

        // Tag the buffer
        Self::tag_buffer(buffer_mut, stream_name);

        // Return the tagged buffer
        Ok(buffer)
    }

    /// Get a pad with the given `pad_name` on the given `aggregator`.
    /// # Arguments
    /// * `aggregator` - The aggregator that holds a pad with the given name.
    /// * `pad_name` - The name of the pad to get.
    #[inline]
    fn get_aggregator_pad(
        aggregator: &gst_base::Aggregator,
        pad_name: &str,
    ) -> gst_base::AggregatorPad {
        aggregator
            .get_static_pad(pad_name)
            .expect(format!("Could not get static pad with name {}", pad_name).as_str())
            .downcast::<gst_base::AggregatorPad>()
            .expect("Could not downcast pad to AggregatorPad")
    }

    /// Tags a `buffer` with a title tag based on the `stream_name`.
    /// # Arguments
    /// * `buffer` - The buffer to tag.
    /// * `stream_name` - The name to use for the title tag.
    #[inline]
    fn tag_buffer(buffer: &mut gst::BufferRef, stream_name: &str) {
        let mut tags = gst::tags::TagList::new();
        tags.make_mut()
            .add::<gst::tags::Title>(&stream_name, gst::TagMergeMode::Append);
        TagsMeta::add(buffer, &mut tags);
    }

    /// Check all sink pads for queued buffers. If one pad has no queued buffer, drop all other buffers and return error.
    /// # Arguments
    /// * `aggregator` - The aggregator to consider.
    /// * `sink_pad_names` - The vector containing all sink pad names.
    #[inline]
    fn drop_buffers_if_one_missing(
        &self,
        aggregator: &gst_base::Aggregator,
        sink_pad_names: &Vec<String>,
    ) -> Result<(), MuxingError> {
        // Iterate over all sink pads
        for sink_pad_name in sink_pad_names.iter() {
            // Get the sink pad given its name
            let sink_pad = Self::get_aggregator_pad(aggregator, sink_pad_name);

            // Check whether the aggregator pad has a buffer available
            if !sink_pad.has_buffer() {
                gst_info!(
                    self.cat,
                    obj: aggregator,
                    "No buffer is queued on `{}` pad. Dropping all other buffers.",
                    sink_pad_name
                );

                // Drop all buffers
                if DROP_ALL_BUFFERS_IF_ONE_IS_MISSING {
                    Self::drop_all_queued_buffers(aggregator, sink_pad_names);
                }

                // Return Err
                return Err(MuxingError(
                    "A pad did not have a queued buffer. Dropped all other buffers.",
                ));
            }
        }
        // Return Ok if all pads have a queued buffer
        Ok(())
    }

    /// Drop all queued buffers on the given `aggregator`.
    /// # Arguments
    /// * `aggregator` - The aggregator to drop all queued buffers for.
    /// * `sink_pad_names` - The vector containing all sink pad names.
    #[inline]
    fn drop_all_queued_buffers(aggregator: &gst_base::Aggregator, sink_pad_names: &Vec<String>) {
        // Iterate over all sink pads
        for sink_pad_name in sink_pad_names.iter() {
            // Get the sink pad given its name
            let sink_pad = Self::get_aggregator_pad(aggregator, sink_pad_name);
            // Drop all buffers present on this pad
            while sink_pad.drop_buffer() {}
        }
    }

    /// Extracts the relevant fields from the pad's CAPS and converts them into a tuple containing
    /// the field's name as the first and its value as second.
    /// # Arguments
    /// * `pad_caps` - A reference to the pad's CAPS.
    /// * `pad_name` - The name of the stream we're currently generating CAPS for.
    #[inline]
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
    #[inline]
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
    #[inline]
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
