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

use gst::{subclass::prelude::*, Event};
use gst_base::prelude::*;
use gst_base::subclass::prelude::*;
use gst_depth_meta::buffer::BufferMeta;
use gst_depth_meta::rgbd;
use gstreamer_base::AggregatorPad;
use once_cell::sync::Lazy;
use std::collections::HashMap;

lazy_static! {
    /// Debug category for 'rgbdmux' element.
    static ref CAT: gst::DebugCategory = gst::DebugCategory::new(
        "rgbdmux",
        gst::DebugColorFlags::empty(),
        Some("RGB-D Muxer"),
    );
}

/// A struct representation of the `rgbdmux` element.
pub struct RgbdMux {}

glib::wrapper! {
    pub struct RgbdMuxObject(ObjectSubclass<RgbdMux>)
        @extends gst_base::Aggregator, gst::Element, gst::Object;
}

#[glib::object_subclass]
impl ObjectSubclass for RgbdMux {
    const NAME: &'static str = "rgbdmux";
    type Type = RgbdMuxObject;
    type ParentType = gst_base::Aggregator;

    fn new() -> Self {
        Self {}
    }
}

impl AggregatorImpl for RgbdMux {
    /// Called whenever a event is received at one of the sink pads.
    /// # Arguments
    /// * `aggregator` - The element that represents the `rgbdmux` in GStreamer.
    /// * `aggregator_pad` - The pad that received the event.
    /// * `event` - The event that should be handled.
    fn sink_event(
        &self,
        aggregator: &RgbdMuxObject,
        aggregator_pad: &AggregatorPad,
        event: Event,
    ) -> bool {
        if let gst::EventView::Tag(_) = event.view() {
            let src_pad = aggregator.static_pad("src").unwrap();
            if !src_pad.push_event(event) {
                gst_warning!(CAT, "Could not send tag event");
            }
            return true;
        }

        self.parent_sink_event(aggregator, aggregator_pad, event)
    }

    /// Called when buffers are queued on all sinkpads. Classes should iterate the GstElement->sinkpads and peek or steal
    /// buffers from the GstAggregatorPad.
    /// # Arguments
    /// * `aggregator` - The element that represents the `rgbdmux` in GStreamer.
    /// * `timeout` - represents if this is the last chance to produce data given the configured framerate
    fn aggregate(
        &self,
        aggregator: &RgbdMuxObject,
        timeout: bool,
    ) -> Result<gst::FlowSuccess, gst::FlowError> {
        // todo::removeme
        gst_error!(
            CAT,
            "aggregator.sink_pads in order: {:?}",
            aggregator
                .sink_pads()
                .iter()
                .map(|pad| pad.name().to_string())
                .collect::<Vec<String>>()
        );
        // Get the current deadline time or desired output time
        let src_pads = aggregator.src_pads();
        let agg_pad = src_pads[0]
            .downcast_ref::<gst_base::AggregatorPad>()
            .unwrap();
        let segment: gst::FormattedSegment<gst::ClockTime> = agg_pad.segment().downcast().unwrap();
        let position_running_time = segment
            .to_running_time(
                segment
                    .position()
                    .unwrap_or_else(|| segment.start().unwrap()),
            )
            .unwrap();
        let duration = RgbdMux::get_duration_from_fps(
            &RgbdMux::get_framerate_from_caps(&agg_pad.caps().unwrap()).unwrap(),
        )
        .unwrap();

        // Analyse all sinkpads for buffers, eos.
        // Notice if all pads have received an EOS message.
        // Drop buffers if their timestamps are out of range.
        let mut all_pads_eos = true;
        let mut all_buffers_in_range = true;
        for sink_pad in aggregator
            .sink_pads()
            .iter()
            .filter_map(|sp| sp.downcast_ref::<gst_base::AggregatorPad>())
        {
            if sink_pad.is_eos() {
                // Nothing for us to do if we have eos on the pad.
                gst_info!(CAT, "Pad {} has EOS", sink_pad.name().to_string());
                continue;
            } else {
                all_pads_eos = false;
            }

            self.pop_out_of_range_buffers_on_pad(&position_running_time, &duration, &sink_pad)?;
            if !sink_pad.has_buffer() {
                // This pad has no buffer, nothing to do for us.
                // Therefore, not all buffer are in range.
                all_buffers_in_range = false;
                continue;
            }
        }

        // Return EOS if all upstream pads are marked as EOS
        if all_pads_eos {
            Err(gst::FlowError::Eos)
        }
        // No buffers yet, nothing to do but wait for more data
        else if !timeout && !all_buffers_in_range {
            Err(gst_base::AGGREGATOR_FLOW_NEED_DATA)
        }
        // We are fully queued, let's push
        else if all_buffers_in_range {
            gst_error!(CAT, "all buffers in range, muxing");
            // https://gstreamer.freedesktop.org/documentation/base/gstaggregator.html?gi-language=c#gst_aggregator_selected_samples
            aggregator.selected_samples(
                position_running_time,
                position_running_time,
                duration,
                None,
            );
            if let Ok(outbuf) = self.mux_buffers(aggregator) {
                self.finish_buffer(aggregator, outbuf)?;
                self.advance_segment_position(aggregator);

                Ok(gst::FlowSuccess::Ok)
            } else {
                // Failed to mux
                self.send_gap_event(aggregator)
                    .map_err(|_| gst::FlowError::Error)?;
                self.advance_segment_position(aggregator);
                Err(gst_base::AGGREGATOR_FLOW_NEED_DATA)
            }
        }
        // timeout, but we are not fully queued. Sending a GAP event
        else if timeout && !all_buffers_in_range {
            self.send_gap_event(aggregator)
                .map_err(|_| gst::FlowError::Error)?;
            self.advance_segment_position(aggregator);
            Err(gst_base::AGGREGATOR_FLOW_NEED_DATA)
        } else {
            panic!("We should never get here")
        }
    }

    /// This function is called during CAPS negotiation. It can be used to decide on a CAPS format
    /// or delay the negotiation until sufficient data is present to decide on the CAPS (in this
    /// case when an upstream element has requested sink pads)
    /// # Arguments
    /// * `aggregator` - A reference to the element that represents `rgbdmux` in GStreamer.
    /// * `_caps` - (not used) The CAPS that is currently negotiated for the element.
    fn update_src_caps(
        &self,
        aggregator: &RgbdMuxObject,
        _caps: &gst::Caps,
    ) -> Result<gst::Caps, gst::FlowError> {
        gst_debug!(CAT, "Updating src CAPS");

        // if no sink pads are present, we're not ready to negotiate CAPS, otherwise do the negotiation
        if aggregator.sink_pads().is_empty() {
            Err(gst_base::AGGREGATOR_FLOW_NEED_DATA) // we're not ready to decide on CAPS yet
        } else {
            self.get_current_downstream_caps(aggregator)
        }
    }

    /// Called when the element needs to know the running time of the next rendered buffer for live pipelines.
    /// Returns the aggregator.simple_get_next_time() unless drop_if_missing is set to false
    /// This causes deadline based aggregation to occur. Returning GST_ClockTime::NONE causes the element to
    /// wait for buffers on all sink pads before aggregating.
    /// # Arguments
    /// * `aggregator` - A reference to the element that represents `rgbdmux` in GStreamer.
    fn next_time(&self, aggregator: &RgbdMuxObject) -> Option<gst::ClockTime> {
        let nt = aggregator.simple_get_next_time();
        gst_error!(
            CAT,
            "Returning next time as {}",
            nt.unwrap_or(gst::ClockTime::ZERO).seconds()
        );
        nt
    }

    /// Called whenever a query is received at one of the sink pads.
    /// CAPS query augmented to use formats for the individual video streams based on requests from the downstream element.
    /// # Arguments
    /// * `aggregator` - The element that represents the `rgbdmux` in GStreamer.
    /// * `aggregator_pad` - The pad that received the query.
    /// * `query` - The query that should be handled.
    fn sink_query(
        &self,
        aggregator: &RgbdMuxObject,
        aggregator_pad: &gst_base::AggregatorPad,
        query: &mut gst::QueryRef,
    ) -> bool {
        #[allow(clippy::single_match)]
        match query.view_mut() {
            gst::QueryView::Caps(mut caps_query) => {
                gst_error!(CAT, "Got caps query on sink pad. Caps: {:?}", caps_query);
                if let Some(filter) = caps_query.filter() {
                    let mut result = filter.copy();
                    let stream_name = aggregator_pad.name().to_string();
                    let stream_name = stream_name.trim_start_matches("sink_");

                    // Get the requested stream formats of downstream element for each stream from video/rgbd CAPS,
                    // translate the format into elementary steam and forward it upstream
                    if let Some(downstream_format) = self
                        .query_downstream_video_formats(aggregator)
                        .get(stream_name)
                    {
                        // Overwrite format, if downstream element requested it
                        for filter_caps in result.get_mut().unwrap().iter_mut() {
                            filter_caps.set::<String>("format", downstream_format.clone());
                        }
                    }

                    caps_query.set_result(&result);
                    true
                } else {
                    // Let parent handle it if there is no filter
                    self.parent_sink_query(aggregator, aggregator_pad, query)
                }
            }
            _ => {
                // Let parent handle all other queries
                self.parent_sink_query(aggregator, aggregator_pad, query)
            }
        }
    }

    /// Called when the src caps have been negotiated
    /// We are setting the latency here.
    fn negotiated_src_caps(
        &self,
        aggregator: &Self::Type,
        caps: &gst::Caps,
    ) -> Result<(), gst::LoggableError> {
        let framerate = RgbdMux::get_framerate_from_caps(caps).unwrap();
        let duration = RgbdMux::get_duration_from_fps(&framerate).unwrap();
        gst_error!(CAT, "Setting latency to {}", duration.seconds());
        aggregator.set_latency(duration, duration);
        self.parent_negotiated_src_caps(aggregator, caps)
    }

    /// Called when the element goes from PAUSED to READY.
    /// # Arguments
    /// * `aggregator` - The element that represents the `rgbdmux` in GStreamer.
    fn stop(&self, aggregator: &RgbdMuxObject) -> Result<(), gst::ErrorMessage> {
        // Reset internals (except for settings)
        self.parent_stop(aggregator)
    }
}

impl ElementImpl for RgbdMux {
    /// This function provides a custom implementation to what should happen when request pads are
    /// released.
    /// # Arguments
    /// * `element` - The element that represents `rgbdmux` in GStreamer.
    /// * `pad` - The pad that is soon to be released.
    fn release_pad(&self, element: &Self::Type, pad: &gst::Pad) {
        // De-activate the pad
        pad.set_active(false)
            .unwrap_or_else(|_| panic!("Could not deactivate a sink pad: {:?}", pad));

        // Remove the pad from the element
        element
            .remove_pad(pad)
            .unwrap_or_else(|_| panic!("Could not remove a sink pad: {:?}", pad));

        // Remove the pad from our internal reference HashMap
        let pad_name = pad.name().as_str().to_string();
        gst_debug!(CAT, obj: element, "release_pad: {}", pad_name);

        // Mark src pad for reconfiguration and let the base class renegotiate right before the next call to aggregate()
        let src_pad = element
            .static_pad("src")
            .expect("rgbdmux: Subclass of GstAggregator must have a src pad");
        src_pad.mark_reconfigure();
    }

    fn metadata() -> Option<&'static gst::subclass::ElementMetadata> {
        static ELEMENT_METADATA: Lazy<gst::subclass::ElementMetadata> = Lazy::new(|| {
            gst::subclass::ElementMetadata::new(
                "RGB-D Muxer",
                "Muxer/RGB-D",
                "Muxes multiple elementary streams into a single `video/rgbd` stream",
                "Andrej Orsula <andrej.orsula@aivero.com>, \
                 Tobias Morell <tobias.morell@aivero.com>, \
                 Raphael Duerscheid <raphael.duerscheid@aivero.com>",
            )
        });

        Some(&*ELEMENT_METADATA)
    }

    fn pad_templates() -> &'static [gst::PadTemplate] {
        static PAD_TEMPLATES: Lazy<[gst::PadTemplate; 2]> = Lazy::new(|| {
            let mut sink_caps = gst::Caps::new_simple("video/x-raw", &[]);
            {
                let sink_caps = sink_caps.get_mut().unwrap();
                sink_caps.append(gst::Caps::new_simple("meta/x-klv", &[("parsed", &true)]));
                sink_caps.append(gst::Caps::new_simple("image/jpeg", &[]));
            }

            [
                gst::PadTemplate::with_gtype(
                    "sink_%s",
                    gst::PadDirection::Sink,
                    gst::PadPresence::Request,
                    &sink_caps,
                    gst_base::AggregatorPad::static_type(),
                )
                .expect("rgbdmux: Failed to add 'sink_%s' pad template"),
                gst::PadTemplate::with_gtype(
                    "src",
                    gst::PadDirection::Src,
                    gst::PadPresence::Always,
                    &gst::Caps::new_simple("video/rgbd", &[]),
                    gst_base::AggregatorPad::static_type(),
                )
                .expect("rgbdmux: Failed to add 'src' pad template"),
            ]
        });

        PAD_TEMPLATES.as_ref()
    }
}

impl RgbdMux {
    /// Advances the segment position of an gst_base::Aggregator's srcpad.segment
    /// This is a requirement for aggregator subclasses that use the `aggregator.simple_get_next_time()`
    /// for the required trait impl function `next_time()`
    /// # Arguments
    /// * `aggregator` - The aggregator to consider.
    fn advance_segment_position(&self, aggregator: &RgbdMuxObject) {
        let src_pads = aggregator.src_pads();
        let agg_pad = src_pads[0]
            .downcast_ref::<gst_base::AggregatorPad>()
            .unwrap();

        let mut segment: gst::FormattedSegment<gst::ClockTime> =
            agg_pad.segment().downcast().unwrap();

        let pts: gst::ClockTime = segment
            .position()
            .unwrap_or_else(|| segment.start().unwrap());

        //todo: Consider bubbling up some error if we fail to get the framerate
        let framerate = RgbdMux::get_framerate_from_caps(&agg_pad.caps().unwrap()).unwrap();
        let duration = RgbdMux::get_duration_from_fps(&framerate);
        let new_position = pts + duration.unwrap_or(gst::ClockTime::ZERO);
        gst_error!(CAT, "Advancing Segment to {}", new_position);
        segment.set_position(new_position);

        // https://gstreamer.freedesktop.org/documentation/base/gstaggregator.html?gi-language=c#gst_aggregator_update_segment
        aggregator.update_segment(&segment);
    }

    /// Look up the framerate from caps on given pad
    /// # Arguments
    /// * `caps` - the caps to look up the framerate on
    /// # Returns:
    /// * Ok(framerate) - if the caps contained a framerate
    /// * Err - if they did not
    fn get_framerate_from_caps(caps: &gst::Caps) -> Result<gst::Fraction, gst::ErrorMessage> {
        let structure = caps.structure(0).unwrap();
        structure
            .get::<gst::Fraction>("framerate")
            .map_err(|e| gst::error_msg!(gst::CoreError::Caps, ["{}", e]))
    }
    /// Converts a framerate specified as a fraction in seconds to a gst::ClockTime
    /// # Arguments
    /// * `framerate` - fraction specified in seconds 30fps -> 30/1
    /// # returns
    /// * Some(duration) - if could convert the fraction to its duration
    /// * None - if the numerator was zero
    fn get_duration_from_fps(framerate: &gst::Fraction) -> Option<gst::ClockTime> {
        gst::ClockTime::SECOND.mul_div_floor(*framerate.denom() as u64, *framerate.numer() as u64)
    }

    /// Pops / removes all buffers from a given pad that are outside of the range
    /// span by `position_running_time ... (position_running_time + duration)
    /// # Arguments
    /// * position_running_time - The current position defined by the aggregator's src_pad.segment
    /// * duration - The inverse of the negotiated framerate for the aggregator's src caps
    /// * sink_pad - The pad on which to check and pop buffers

    fn pop_out_of_range_buffers_on_pad(
        &self,
        position_running_time: &gst::ClockTime,
        duration: &gst::ClockTime,
        sink_pad: &gst_base::AggregatorPad,
    ) -> Result<(), gst::FlowError> {
        while let Some(buffer) = sink_pad.peek_buffer() {
            let segment = sink_pad.segment().downcast::<gst::ClockTime>().unwrap();
            if buffer.pts().is_none() {
                return Err(gst::FlowError::Error);
            }
            let buffer_running_time = segment
                .to_running_time(buffer.pts())
                .unwrap_or(gst::ClockTime::ZERO);

            // Buffers TS are in range if they are equal to the current deadline or in the future,
            // but not more than `duration` in the future.
            //  if(buffer_running_time >= *position_running_time
            //     && buffer_running_time < position_running_time + duration){
            //     valid_buffer
            // }

            if buffer_running_time < *position_running_time
                || buffer_running_time >= (position_running_time + duration)
            {
                sink_pad.drop_buffer();
                gst_error!(CAT, "Buffer out of time, dropping it");
            } else {
                gst_error!(CAT, "Buffer in range");
                // This buffer is in range, lets return;
                break;
            }
        }
        Ok(())
    }
    /// Mux all buffers to a single output buffer. All buffers are properly tagget with a title.
    /// # Arguments
    /// * `aggregator` - The aggregator to consider.
    /// # Returns:
    /// * OK(buf) - The main buffer, containing aux buffers as BufferMeta
    /// * Err
    fn mux_buffers(&self, aggregator: &RgbdMuxObject) -> Result<gst::Buffer, gst::ErrorMessage> {
        let sink_pads = aggregator.sink_pads();
        let mut sink_pads = sink_pads
            .iter()
            .filter_map(|sp| sp.downcast_ref::<gst_base::AggregatorPad>());

        // Use the first buffer in the aggregator.sink_pads as the buffer we send out
        let first_pad = sink_pads.next().unwrap();
        let first_pad_name = first_pad.name().to_string();

        let mut main_buffer = match first_pad.pop_buffer() {
            // We have a buffer, let's tag it
            Some(mut buf) => {
                let stream_name = first_pad_name.trim_start_matches("sink_");
                rgbd::tag_buffer_with_title(buf.make_mut(), stream_name)?;
                buf
            }
            // There is no buffer, let's send a gap event
            None => {
                return Err(gst::error_msg!(gst::CoreError::Pad, ["No buffer found"]));
            }
        };

        // Iterate over all other sink pads, excluding the first one (already processed)
        // For each pad, get a tagged buffer and attach it to the main buffer
        // If a sink pad has no buffer queued, create an empty GAP buffer and attach it to the main buffer as well
        for agg_pad in sink_pads {
            self.attach_aux_buffers(agg_pad, main_buffer.make_mut())?;
        }

        gst_debug!(CAT, obj: aggregator, "A frameset was muxed.");
        Ok(main_buffer)
    }

    /// Get a tagged buffer from pad `sink_pad_name` and attach it to `main_buffer`. If a sink pad has no buffer queued,
    /// create an empty GAP buffer and attach it to the main buffer as well.
    /// # Arguments
    /// * `aggregator` - The aggregator to consider.
    /// * `sink_pad_names` - The vector containing all sink pad names.
    /// * `main_buffer` - Mutable reference to the main buffer to which we attach all auxiliary buffers.
    fn attach_aux_buffers(
        &self,
        sink_pad: &AggregatorPad,
        main_buffer: &mut gst::BufferRef,
    ) -> Result<(), gst::ErrorMessage> {
        let stream_name = sink_pad.name();
        let stream_name = stream_name.as_str().trim_start_matches("sink_");
        match sink_pad.pop_buffer() {
            Some(mut buffer) => {
                rgbd::tag_buffer_with_title(buffer.make_mut(), stream_name)?;
                BufferMeta::add(main_buffer, &mut buffer);
                Ok(())
            }
            None => {
                return Err(gst::error_msg!(
                    gst::CoreError::Pad,
                    ["No buffer is queued on auxiliary `{}` pad.", stream_name]
                ))
            }
        }
    }

    /// Sends a gap event downstream.
    /// # Arguments
    /// * `aggregator` - The aggregator to drop all queued buffers for.
    fn send_gap_event(&self, aggregator: &RgbdMuxObject) -> Result<(), gst::ErrorMessage> {
        gst_error!(CAT, "sending gap event");
        // Get the current position aka deadline as
        let src_pads = aggregator.src_pads();
        let agg_pad: &gst_base::AggregatorPad = src_pads[0].downcast_ref().unwrap();

        let segment: gst::FormattedSegment<gst::ClockTime> = agg_pad.segment().downcast().unwrap();
        let pts: gst::ClockTime = segment
            .position()
            .unwrap_or_else(|| segment.start().unwrap());
        let running_time = segment.to_running_time(pts).unwrap();

        let framerate = RgbdMux::get_framerate_from_caps(&agg_pad.caps().unwrap())?;
        let duration = RgbdMux::get_duration_from_fps(&framerate);

        // Create a GAP event with duration
        let gap_event = gst::event::Gap::new(running_time, duration);

        // And send it downstream
        if aggregator.send_event(gap_event) {
            gst_debug!(CAT, obj: aggregator, "Sending of GAP event was successful");
            Ok(())
        } else {
            gst_warning!(CAT, obj: aggregator, "Failed to send gap event");
            Err(gst::error_msg!(gst::CoreError::Event, [""]))
        }
    }

    /// Extracts the relevant fields from the pad's CAPS and converts them into a tuple containing
    /// the field's name as the first and its value as second.
    /// # Arguments
    /// * `pad_caps` - A reference to the pad's CAPS.
    /// * `pad_name` - The name of the stream we're currently generating CAPS for.
    fn compose_elementary_caps_to_rgbd_caps(
        &self,
        pad_caps: &gst::Caps,
        pad_name: &str,
        src_caps: &mut gst::StructureRef,
    ) {
        let stream_name = &pad_name[5..];
        // Set the format for MJPG stream
        if pad_caps.is_subset(gst::Caps::new_simple("image/jpeg", &[]).as_ref()) {
            let src_field_name = format!("{}_format", stream_name);
            src_caps.set(&src_field_name, &"image/jpeg");
        }

        // Filter out all CAPS we don't care about and map those we do into strings
        let pad_caps = pad_caps.iter().next().expect("rgbdmux: Got empty CAPS");
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
                        CAT,
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
    fn get_current_downstream_caps(
        &self,
        aggregator: &RgbdMuxObject,
    ) -> Result<gst::Caps, gst::FlowError> {
        // Join all the pad names to create the 'streams' section of the CAPS
        let sink_pads = aggregator.sink_pads();
        let sink_pads = sink_pads
            .iter()
            .filter_map(|pad| pad.downcast_ref::<gst_base::AggregatorPad>());

        let sink_pad_names: Vec<String> = sink_pads
            .clone()
            .map(|pad| pad.name().to_string())
            .collect();
        let streams = sink_pad_names
            .iter()
            .map(|s| s.as_str().trim_start_matches("sink_"))
            .collect::<Vec<&str>>()
            .join(",");

        // Find the lowest framerate defined across all the caps of our sinkpads
        // The framerate is the lowest framerate found across all sinkpads,
        // since we will drop all frames if one frame is missing
        let min_framerate = sink_pads
            .clone()
            .filter_map(|pad| {
                let caps = pad.caps()?;
                let structure = caps.structure(0)?;
                structure.get::<gst::Fraction>("framerate").ok()
            })
            .min();
        if min_framerate.is_none() {
            gst_warning!(
                CAT,
                "Sinkpads' caps do not contain any framerate. Might be too early."
            );
            return Err(gst_base::AGGREGATOR_FLOW_NEED_DATA);
        }
        let mut downstream_caps = gst::Caps::new_simple(
            "video/rgbd",
            &[
                ("streams", &streams),
                ("framerate", &min_framerate.unwrap()),
            ],
        );

        let mut_caps = downstream_caps
            .make_mut()
            .structure_mut(0)
            .expect("rgbdmux: Could not get mutable CAPS");

        // Map the caps into their corresponding stream formats
        for (caps, pad_name) in sink_pads
            // Only handle pads with caps
            .filter_map(|agg_pad| {
                if agg_pad.current_caps().is_some() {
                    Some((agg_pad.current_caps().unwrap(), agg_pad.name().to_string()))
                } else {
                    None
                }
            })
        {
            // Add the elementary caps to the main caps
            self.compose_elementary_caps_to_rgbd_caps(&caps, &pad_name, mut_caps)
        }
        gst_info!(
            CAT,
            obj: aggregator,
            "stream_caps were found to be: {:?}.",
            downstream_caps
        );

        Ok(downstream_caps.to_owned())
    }

    /// Query downstream element of `aggregator` for CAPS and extracts format fields for each stream.
    /// # Arguments
    /// * `aggregator` - The aggregator that represents `rgbdmux`.
    /// # Returns
    /// * `HashMap<String, String>` - Hashmap containing <stream, format>.
    fn query_downstream_video_formats(
        &self,
        aggregator: &RgbdMuxObject,
    ) -> HashMap<String, String> {
        let src_pad = aggregator
            .static_pad("src")
            .expect("rgbdmux: Element must have a src pad to receive a src_query");
        let src_pad_template_caps = aggregator
            .pad_template("src")
            .expect("rgbdmux: Could not find src-pad template")
            .caps();

        // Create CAPS query with filter based on template CAPS
        let mut request_downstream_caps_query = gst::query::Caps::new(Some(&src_pad_template_caps));

        // Send the query and receive sink CAPS of the downstream element
        if !src_pad.peer_query(&mut request_downstream_caps_query) {
            gst_debug!(
                CAT,
                obj: aggregator,
                "Cannot send CAPS query downstream. The src pad of this element is probably not yet linked.",
            );
            return HashMap::new();
        }

        if let Some(requested_caps) = request_downstream_caps_query.result() {
            // We can only handle fixed CAPS here
            if !requested_caps.is_fixed() {
                gst_debug!(
                    CAT,
                    obj: aggregator,
                    "Downstream element queried CAPS that are NOT fixed. Only fixed `video/rgbd` CAPS can be handled properly.",
                );
                return HashMap::new();
            }

            // Extract formats from these caps for use when creating new CAPS
            self.extract_formats_from_rgbd_caps(requested_caps)
        } else {
            gst_warning!(
                CAT,
                obj: aggregator,
                "Downstream element did not return a valid result for CAPS query.",
            );
            HashMap::new()
        }
    }

    /// Extracts format field for each stream in `video/rgbd` CAPS.
    /// # Arguments
    /// * `caps` - Formats are extracted from these `video/rgbd` CAPS.
    /// # Returns
    /// * `HashMap<String, String>` - Hashmap containing <stream, format>.
    fn extract_formats_from_rgbd_caps(&self, caps: &gst::CapsRef) -> HashMap<String, String> {
        // Iterate over all fields in the input CAPS and retain only the format field
        caps.iter()
            .next()
            .expect("rgbdmux: Downstream element has not CAPS")
            .iter()
            .filter_map(|(field, value)| {
                if !field.contains("_format") {
                    None
                } else {
                    Some((field.replace("_format", ""), value.get::<String>().unwrap()))
                }
            })
            .collect::<HashMap<String, String>>()
    }
}

impl ObjectImpl for RgbdMux {
    fn constructed(&self, obj: &Self::Type) {
        self.parent_constructed(obj);
        // obj.set_start_time_selection(gst_base::AggregatorStartTimeSelection::First);
    }
}

pub fn register(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    gst::Element::register(Some(plugin), "rgbdmux", gst::Rank::None, RgbdMux::type_())
}
