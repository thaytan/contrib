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
use gst_depth_meta::rgbd;
use std::collections::HashMap;
use std::sync::{Mutex, RwLock};

use super::clock_internals::*;
use super::error::*;
use super::properties::*;
use crate::common::*;

lazy_static! {
    /// Debug category for 'rgbdmux' element.
    pub(crate) static ref CAT: gst::DebugCategory = gst::DebugCategory::new(
        "rgbdmux",
        gst::DebugColorFlags::empty(),
        Some("RGB-D Muxer"),
    );
}

/// A struct representation of the `rgbdmux` element.
struct RgbdMux {
    /// Settings based on properties of the element.
    settings: RwLock<Settings>,
    /// Clock internals of the element.
    clock_internals: RwLock<ClockInternals>,
    /// List of sink pad names that this muxer contains.
    sink_pad_names: Mutex<Vec<String>>,
}

impl ObjectSubclass for RgbdMux {
    const NAME: &'static str = "rgbdmux";
    type ParentType = gst_base::Aggregator;
    type Instance = gst::subclass::ElementInstanceStruct<Self>;
    type Class = subclass::simple::ClassStruct<Self>;

    glib_object_subclass!();

    fn new() -> Self {
        Self {
            settings: RwLock::new(Settings::default()),
            clock_internals: RwLock::new(ClockInternals::default()),
            sink_pad_names: Mutex::new(Vec::new()),
        }
    }

    fn class_init(klass: &mut subclass::simple::ClassStruct<Self>) {
        klass.set_metadata(
            "RGB-D Muxer",
            "Muxer/RGB-D",
            "Muxes multiple elementary streams into a single `video/rgbd` stream",
            "Andrej Orsula <andrej.orsula@aivero.com>, Tobias Morell <tobias.morell@aivero.com>",
        );

        klass.install_properties(&PROPERTIES);

        // Sink pads
        let mut sink_caps = gst::Caps::new_simple("video/x-raw", &[]);
        {
            let sink_caps = sink_caps.get_mut().unwrap();
            sink_caps.append(gst::Caps::new_simple("meta/x-klv", &[("parsed", &true)]));
            sink_caps.append(gst::Caps::new_simple("image/jpeg", &[]));
        }

        klass.add_pad_template(
            gst::PadTemplate::with_gtype(
                "sink_%s",
                gst::PadDirection::Sink,
                gst::PadPresence::Request,
                &sink_caps,
                gst_base::AggregatorPad::static_type(),
            )
            .expect("rgbdmux: Failed to add 'sink_%s' pad template"),
        );

        // Src pad
        klass.add_pad_template(
            gst::PadTemplate::with_gtype(
                "src",
                gst::PadDirection::Src,
                gst::PadPresence::Always,
                &gst::Caps::new_simple("video/rgbd", &[]),
                gst_base::AggregatorPad::static_type(),
            )
            .expect("rgbdmux: Failed to add 'src' pad template"),
        );
    }
}

impl AggregatorImpl for RgbdMux {
    /// Called when buffers are queued on all sinkpads. Classes should iterate the GstElement->sinkpads and peek or steal
    /// buffers from the GstAggregatorPad.
    /// # Arguments
    /// * `aggregator` - The element that represents the `rgbdmux` in GStreamer.
    fn aggregate(
        &self,
        aggregator: &gst_base::Aggregator,
        _timeout: bool,
    ) -> Result<gst::FlowSuccess, gst::FlowError> {
        let sink_pad_names = self.sink_pad_names.lock().unwrap();

        // Return EOS if all upstream pads are marked as EOS
        if sink_pad_names
            .iter()
            .all(|pad_name| Self::get_aggregator_pad(aggregator, pad_name).is_eos())
        {
            return Err(gst::FlowError::Eos);
        }

        // Check if all pads have valid buffers before muxing them
        {
            let settings = self.settings.read().unwrap();
            // Check all sink pads for queued buffers. If one pad has no queued buffer, drop all other buffers.
            if settings.drop_if_missing {
                if self
                    .drop_buffers_if_one_missing(
                        aggregator,
                        &sink_pad_names,
                        settings.send_gap_events,
                    )
                    .is_err()
                {
                    return Ok(gst::FlowSuccess::Ok);
                }
            }

            // Make sure the streams are synchronised
            if settings.drop_to_synchronise {
                let ret = self.check_synchronisation(
                    aggregator,
                    &sink_pad_names,
                    settings.send_gap_events,
                );
                if ret.is_err() {
                    return Ok(gst::FlowSuccess::Ok);
                }
            }
        }

        // Mux all buffers to a single output buffer
        let output_buffer = self.mux_buffers(aggregator, &sink_pad_names);
        drop(sink_pad_names);

        // Finish the buffer if all went fine
        self.finish_buffer(aggregator, output_buffer)
    }

    /// This function is called when a peer element requests a pad. It provides a custom implementation
    /// for how the pad should be created.
    /// # Arguments
    /// * `aggregator` - The element that represents the `rgbdmux` in GStreamer.
    /// * `templ` - The template that should be used in pad creation.
    /// * `req_name` - The requested name for the pad.
    /// * `_caps` - (not used) The CAPS to use for the pad.
    fn create_new_pad(
        &self,
        aggregator: &gst_base::Aggregator,
        templ: &gst::PadTemplate,
        req_name: Option<&str>,
        _caps: Option<&gst::Caps>,
    ) -> Option<gst_base::AggregatorPad> {
        let name = req_name?;
        if !name.starts_with("sink_") {
            gst_error!(
                CAT,
                obj: aggregator,
                "Pad was requested with an invalid name, please use template 'sink_%s'"
            );
            return None;
        }
        gst_debug!(CAT, obj: aggregator, "Creating new {} pad", name);

        // Create new sink pad from the template
        let mut sink_pad_names = self.sink_pad_names.lock().unwrap();
        let new_sink_pad = gst::Pad::from_template(templ, Some(name))
            .downcast::<gst_base::AggregatorPad>()
            .expect("rgbdmux: Could not cast GstPad to GstAggregatorPad");

        // Insert the new sink pad name into the struct
        sink_pad_names.push(name.to_string());

        // Activate the sink pad
        new_sink_pad
            .set_active(true)
            .expect("rgbdmux: Failed to activate sink pad");

        Some(new_sink_pad)
    }

    /// This function is called during CAPS negotiation. It can be used to decide on a CAPS format
    /// or delay the negotiation until sufficient data is present to decide on the CAPS (in this
    /// case when an upstream element has requested sink pads)
    /// # Arguments
    /// * `aggregator` - A reference to the element that represents `rgbdmux` in GStreamer.
    /// * `_caps` - (not used) The CAPS that is currently negotiated for the element.
    fn update_src_caps(
        &self,
        aggregator: &gst_base::Aggregator,
        _caps: &gst::Caps,
    ) -> Result<gst::Caps, gst::FlowError> {
        gst_debug!(CAT, "Updating src CAPS");
        let sink_pad_names = self.sink_pad_names.lock().unwrap();

        // if no sink pads are present, we're not ready to negotiate CAPS, otherwise do the negotiation
        if sink_pad_names.is_empty() {
            Err(gst_base::AGGREGATOR_FLOW_NEED_DATA) // we're not ready to decide on CAPS yet
        } else {
            Ok(self.get_current_downstream_caps(
                aggregator.upcast_ref::<gst::Element>(),
                &sink_pad_names,
            ))
        }
    }

    /// Called when the element needs to know the running time of the next rendered buffer for live pipelines.
    /// This causes deadline based aggregation to occur. Returning GST_CLOCK_TIME_NONE causes the element to
    /// wait for buffers on all sink pads before aggregating.
    /// # Arguments
    /// * `aggregator` - A reference to the element that represents `rgbdmux` in GStreamer.
    fn get_next_time(&self, aggregator: &gst_base::Aggregator) -> gst::ClockTime {
        if self.settings.read().unwrap().drop_if_missing {
            let clock_internals = self.clock_internals.read().unwrap();
            if clock_internals.previous_timestamp != gst::CLOCK_TIME_NONE {
                // Return deadline for the aggregation
                return clock_internals.previous_timestamp + clock_internals.deadline_duration;
            }
        }
        // Else, chain up the parent implementation
        self.parent_get_next_time(aggregator)
    }

    /// Called whenever a query is received at one of the sink pads.
    /// CAPS query augmented to use formats for the individual video streams based on requests from the downstream element.
    /// # Arguments
    /// * `aggregator` - The element that represents the `rgbdmux` in GStreamer.
    /// * `aggregator_pad` - The pad that received the query.
    /// * `query` - The query that should be handled.
    fn sink_query(
        &self,
        aggregator: &gst_base::Aggregator,
        aggregator_pad: &gst_base::AggregatorPad,
        query: &mut gst::QueryRef,
    ) -> bool {
        #[allow(clippy::single_match)]
        match query.view_mut() {
            gst::QueryView::Caps(mut caps_query) => {
                if let Some(filter) = caps_query.get_filter() {
                    let mut result = filter.copy();
                    let stream_name = &aggregator_pad.get_name()[5..];

                    // Get the requested stream formats of downstream element for each stream from video/rgbd CAPS,
                    // translate the format into elementary steam and forward it upstream
                    if let Some(downstream_format) = self
                        .query_downstream_video_formats(aggregator)
                        .get(stream_name)
                    {
                        // Overwrite format, if downstream element requested it
                        for filter_caps in result.get_mut().unwrap().iter_mut() {
                            filter_caps.set::<String>("format", downstream_format);
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

    /// Called when the element goes from PAUSED to READY.
    /// # Arguments
    /// * `aggregator` - The element that represents the `rgbdmux` in GStreamer.
    fn stop(&self, aggregator: &gst_base::Aggregator) -> Result<(), gst::ErrorMessage> {
        // Reset internals (except for settings)
        *self.clock_internals.write().unwrap() = ClockInternals::default();
        self.sink_pad_names.lock().unwrap().clear();

        self.parent_stop(aggregator)
    }
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
            .unwrap_or_else(|_| panic!("Could not deactivate a sink pad: {:?}", pad));

        // Remove the pad from the element
        element
            .remove_pad(pad)
            .unwrap_or_else(|_| panic!("Could not remove a sink pad: {:?}", pad));

        // Remove the pad from our internal reference HashMap
        let pad_name = pad.get_name().as_str().to_string();
        gst_debug!(CAT, obj: element, "release_pad: {}", pad_name);
        {
            self.sink_pad_names
                .lock()
                .unwrap()
                .retain(|x| *x != pad_name);
        }

        // Mark src pad for reconfiguration and let the base class renegotiate right before the next call to aggregate()
        let src_pad = element
            .get_static_pad("src")
            .expect("rgbdmux: Subclass of GstAggregator must have a src pad");
        src_pad.mark_reconfigure();
    }
}

impl RgbdMux {
    /// Mux all buffers to a single output buffer. All buffers are properly tagget with a title.
    /// # Arguments
    /// * `aggregator` - The aggregator to consider.
    /// * `sink_pad_names` - The vector containing all sink pad names.
    fn mux_buffers(
        &self,
        aggregator: &gst_base::Aggregator,
        sink_pad_names: &[String],
    ) -> gst::Buffer {
        // Place a buffer from the first pad into the main buffer
        // If there is no buffer, leave the main buffer empty and flag it as GAP
        let mut main_buffer = Self::get_tagged_buffer(aggregator, &sink_pad_names[0])
            .unwrap_or_else(|_e| {
                gst_warning!(
                    CAT,
                    obj: aggregator,
                    "No buffer is queued on main `{}` pad. Sending GAP buffer downstream.",
                    sink_pad_names[0]
                );
                Self::new_tagged_gap_buffer(&sink_pad_names[0])
            });

        // Get a mutable reference to the main buffer
        let main_buffer_mut = {
            if let Some(buffer_mut) = main_buffer.get_mut() {
                buffer_mut
            } else {
                main_buffer.make_mut()
            }
        };

        // Update the current timestamp (make sure the timestamp is valid)
        let mut clock_internals = self.clock_internals.write().unwrap();
        clock_internals.previous_timestamp = main_buffer_mut.get_pts();

        // Iterate over all other sink pads, excluding the first one (already processed)
        // For each pad, get a tagged buffer and attach it to the main buffer
        // If a sink pad has no buffer queued, create an empty GAP buffer and attach it to the main buffer as well
        for sink_pad_name in sink_pad_names.iter().skip(1) {
            self.attach_aux_buffers(
                aggregator,
                &mut clock_internals,
                sink_pad_name,
                main_buffer_mut,
            );
        }

        // Reset GAP event flag on successful aggregation
        clock_internals.is_gap_event_sent = false;

        gst_debug!(CAT, obj: aggregator, "A frameset was muxed.");
        main_buffer
    }

    /// Get a tagged buffer from pad `sink_pad_name` and attach it to `main_buffer`. If a sink pad has no buffer queued,
    /// create an empty GAP buffer and attach it to the main buffer as well.
    /// # Arguments
    /// * `aggregator` - The aggregator to consider.
    /// * `sink_pad_names` - The vector containing all sink pad names.
    /// * `clock_internals` - Mutable reference to the clock internals of `rgbdmux`.
    /// * `main_buffer` - Mutable reference to the main buffer to which we attach all auxiliary buffers.
    fn attach_aux_buffers(
        &self,
        aggregator: &gst_base::Aggregator,
        clock_internals: &mut ClockInternals,
        sink_pad_name: &String,
        main_buffer: &mut gst::BufferRef,
    ) {
        match Self::get_tagged_buffer(aggregator, sink_pad_name) {
            Ok(mut buffer) => {
                {
                    if clock_internals.previous_timestamp == gst::CLOCK_TIME_NONE {
                        clock_internals.previous_timestamp = buffer.get_mut().unwrap().get_pts();
                    }
                }
                BufferMeta::add(main_buffer, &mut buffer);
            }
            Err(_) => {
                gst_warning!(
                    CAT,
                    obj: aggregator,
                    "No buffer is queued on auxiliary `{}` pad. Attaching GAP buffer with corresponding tag to the main buffer.",
                    sink_pad_name
                );
                BufferMeta::add(
                    main_buffer,
                    &mut Self::new_tagged_gap_buffer(&sink_pad_name),
                );
            }
        }
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
            .unwrap_or_else(|| panic!("Could not get static pad with name {}", pad_name))
            .downcast::<gst_base::AggregatorPad>()
            .expect("rgbdmux: Cannot downcast GstPad to GstAggregatorPad")
    }

    /// Get a buffer from the pad with the given `pad_name` on the given `aggregator`. This function
    /// also tags the buffer with a correct title tag.
    /// # Arguments
    /// * `aggregator` - The aggregator that holds a pad with the given name.
    /// * `pad_name` - The name of the pad to read a buffer from.
    fn get_tagged_buffer(
        aggregator: &gst_base::Aggregator,
        pad_name: &str,
    ) -> Result<gst::Buffer, RgbdMuxError> {
        // Get the sink pad given its name
        let sink_pad = Self::get_aggregator_pad(aggregator, pad_name);

        // Extract a buffer from the given sink pad
        let mut buffer = sink_pad
            .pop_buffer()
            .ok_or_else(|| RgbdMuxError("No buffer queued on one of the pads".to_string()))?;

        // Get a mutable reference to the buffer
        let buffer_mut = if let Some(buffer_mut) = buffer.get_mut() {
            buffer_mut
        } else {
            buffer.make_mut()
        };

        // Get the stream name by truncating the "sink_" prefix
        let stream_name = &pad_name[5..];
        // Tag the buffer
        rgbd::tag_buffer(buffer_mut, stream_name)?;

        // Return the tagged buffer
        Ok(buffer)
    }

    /// Create a new empty buffer, that is flagged as GAP and DROPPABLE. This function
    /// also tags the buffer with a correct title tag.
    /// # Arguments
    /// * `pad_name` - The name of the pad to read a buffer from.
    fn new_tagged_gap_buffer(pad_name: &str) -> gst::Buffer {
        let mut buffer = gst::Buffer::new();
        // Get mutable reference the newly created buffer, which is always writable
        let buffer_mut = buffer.get_mut().unwrap();
        // Set the GAP flag
        buffer_mut.set_flags(gst::BufferFlags::GAP | gst::BufferFlags::DROPPABLE);

        // Truncate "sink_" prefix and tag the buffer
        let stream_name = &pad_name[5..];
        rgbd::tag_buffer(buffer_mut, stream_name)
            .expect("rgbdmux: An empty buffer could not be tagged");
        buffer
    }

    /// Check all sink pads for queued buffers. If one pad has no queued buffer, drop all other buffers and return error.
    /// # Arguments
    /// * `aggregator` - The aggregator to consider.
    /// * `sink_pad_names` - The vector containing all sink pad names.
    /// * `send_gap_event` - A flag that determines whether to send gap event when buffers are dropped.
    /// # Returns
    /// * `Err(RgbdMuxError)` - If one or more buffers are missing.
    fn drop_buffers_if_one_missing(
        &self,
        aggregator: &gst_base::Aggregator,
        sink_pad_names: &[String],
        send_gap_event: bool,
    ) -> Result<(), RgbdMuxError> {
        // First check if any of the sink pads have any buffer queued
        if !sink_pad_names
            .iter()
            .any(|sink_pad_name| Self::get_aggregator_pad(aggregator, sink_pad_name).has_buffer())
        {
            return Err(RgbdMuxError("No buffers are queued, skipping".to_string()));
        }

        // If yes, iterate over all sink pads and figure out if any is missing
        for sink_pad_name in sink_pad_names.iter() {
            // Get the sink pad given its name
            let sink_pad = Self::get_aggregator_pad(aggregator, sink_pad_name);

            // Check whether the aggregator pad has a buffer available
            if !sink_pad.has_buffer() {
                gst_warning!(
                    CAT,
                    obj: aggregator,
                    "No buffer is queued on `{}` pad. Dropping a single buffer on all other pads.",
                    sink_pad_name
                );

                // Drop all buffers
                self.drop_all_queued_buffers(aggregator, sink_pad_names);

                // Send gap event downstream
                if send_gap_event {
                    self.send_gap_event(aggregator);
                }

                // Set previous timestamp to CLOCK_TIME_NONE if any buffers had to be dropped
                {
                    let mut clock_internals = self.clock_internals.write().unwrap();
                    clock_internals.previous_timestamp = gst::CLOCK_TIME_NONE;
                }

                // Return Err
                return Err(RgbdMuxError(
                    "One of the pads did not have a queued buffer. Dropped all other buffers."
                        .to_string(),
                ));
            }
        }
        // Return Ok if all pads have a queued buffer
        Ok(())
    }

    /// Drop a single buffer on all queued aggregator sink pads.
    /// # Arguments
    /// * `aggregator` - The aggregator to drop all queued buffers for.
    /// * `sink_pad_names` - The vector containing all sink pad names.
    fn drop_all_queued_buffers(
        &self,
        aggregator: &gst_base::Aggregator,
        sink_pad_names: &[String],
    ) {
        // Iterate over all sink pads
        for sink_pad_name in sink_pad_names.iter() {
            // Get the sink pad given its name
            let sink_pad = Self::get_aggregator_pad(aggregator, sink_pad_name);
            // Drop the buffer present on this pad
            sink_pad.drop_buffer();
        }
    }

    /// Check whether the streams are synchronised based on their pts timestamps.
    /// If the streams are not synchronised, buffers that are behind get dropped and error is returned.
    /// # Arguments
    /// * `aggregator` - The aggregator to consider.
    /// * `sink_pad_names` - The vector containing all sink pad names.
    /// * `send_gap_event` - A flag that determines whether to send gap event when buffers are dropped.
    /// # Returns
    /// * `Err(RgbdMuxError)` - If frames are not synchronised.
    fn check_synchronisation(
        &self,
        aggregator: &gst_base::Aggregator,
        sink_pad_names: &[String],
        send_gap_event: bool,
    ) -> Result<(), RgbdMuxError> {
        let mut timestamps: Vec<(String, gst::ClockTime)> =
            self.get_timestamps(aggregator, sink_pad_names);

        if timestamps.is_empty() {
            gst_warning!(
                CAT,
                obj: aggregator,
                "Synchronisation failed because no buffer is queued."
            );
            return Err(RgbdMuxError(
                "Synchronisation failed because no buffer is queued.".to_string(),
            ));
        }

        // Get the min and max timestamps of the queued buffers
        timestamps
            .sort_by(|(_, t1), (_, t2)| t1.partial_cmp(t2).unwrap_or(std::cmp::Ordering::Equal));
        let (_, min_pts) = timestamps.first().unwrap();
        let (_, max_pts) = timestamps.last().unwrap();

        // Check if all timestamps are synchronised
        if self
            .clock_internals
            .read()
            .unwrap()
            .is_synchronised(min_pts, max_pts)
        {
            return Ok(());
        }

        // If the streams are not synchronised, iterature over all buffers and
        // drop a single buffer for those that are late
        for (sink_pad_name, timestamp) in timestamps.iter() {
            if timestamp < max_pts {
                // Get sink pad with the given name
                let sink_pad = Self::get_aggregator_pad(aggregator, sink_pad_name);
                // Drop the buffer
                sink_pad.drop_buffer();
            } else {
                // Timestamps are sorted, therefore we can break here
                break;
            }
        }

        // Send gap event downstream
        if send_gap_event {
            self.send_gap_event(aggregator);
        }

        // Set previous timestamp to CLOCK_TIME_NONE if any buffers had to be dropped
        {
            let mut clock_internals = self.clock_internals.write().unwrap();
            clock_internals.previous_timestamp = gst::CLOCK_TIME_NONE;
        }

        gst_warning!(
            CAT,
            obj: aggregator,
            "Timestamps on the received buffers do not match. Dropped some buffer(s) to synchronise the streams"
        );

        // Return error
        Err(RgbdMuxError(
            "Dropped buffers to synchronise the streams".to_string(),
        ))
    }

    /// Returns timestamps of buffers queued on the sink pads
    /// # Arguments
    /// * `aggregator` - The aggregator to consider.
    /// * `sink_pad_names` - The vector containing all sink pad names.
    /// # Returns
    /// * `Vec<(String, gst::ClockTime)>` - A pair if sink pad names and the corresponding pts
    fn get_timestamps(
        &self,
        aggregator: &gst_base::Aggregator,
        sink_pad_names: &[String],
    ) -> Vec<(String, gst::ClockTime)> {
        sink_pad_names
            .iter()
            // Extract aggregator pads based on their names
            .map(|sink_pad_name| {
                (
                    sink_pad_name,
                    Self::get_aggregator_pad(aggregator, sink_pad_name),
                )
            })
            // Get buffers if they are queued on the pads
            .filter_map(|(sink_pad_name, sink_pad)| match sink_pad.peek_buffer() {
                Some(buffer) => Some((sink_pad_name, buffer)),
                _ => None,
            })
            // Get pts timestamps for all buffers and collect into vector
            .map(|(sink_pad_name, buffer)| (sink_pad_name.to_string(), buffer.get_pts()))
            .collect::<Vec<(String, gst::ClockTime)>>()
    }

    /// Sends a gap event downstream.
    /// # Arguments
    /// * `aggregator` - The aggregator to drop all queued buffers for.
    fn send_gap_event(&self, aggregator: &gst_base::Aggregator) {
        let mut clock_internals = self.clock_internals.write().unwrap();

        // Return if GAP event was already sent for this sequence of consecutive calls
        // Hint: is_gap_event_sent is reset to false on successful aggregation.
        if clock_internals.is_gap_event_sent {
            return;
        }
        clock_internals.is_gap_event_sent = true;

        // Make sure the previous timestamp is valid
        if clock_internals.previous_timestamp == gst::CLOCK_TIME_NONE {
            gst_error!(
                CAT,
                obj: aggregator,
                "GAP event could not be sent, because the previous frameset timestamp is NOT valid",
            );
            return;
        }

        // Create a GAP event with unknown duration
        let gap_event =
            gst::event::Gap::builder(clock_internals.previous_timestamp, gst::CLOCK_TIME_NONE)
                .build();

        // Drop internals before sending the event
        drop(clock_internals);

        // And send it downstream
        if aggregator.send_event(gap_event) {
            gst_debug!(CAT, obj: aggregator, "Sending of GAP event was successful");
        } else {
            gst_warning!(CAT, obj: aggregator, "Failed to send gap event");
        }
    }

    /// Extracts the relevant fields from the pad's CAPS and converts them into a tuple containing
    /// the field's name as the first and its value as second.
    /// # Arguments
    /// * `pad_caps` - A reference to the pad's CAPS.
    /// * `pad_name` - The name of the stream we're currently generating CAPS for.
    fn elementary_caps_to_rgbd(
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
                    src_caps.set(
                        &src_field_name,
                        &value.get::<&str>().unwrap().unwrap_or_default(),
                    );
                }
                "width" => {
                    let src_field_name = format!("{}_{}", stream_name, field);
                    src_caps.set(&src_field_name, &value.get_some::<i32>().unwrap());
                }
                "height" => {
                    let src_field_name = format!("{}_{}", stream_name, field);
                    src_caps.set(&src_field_name, &value.get_some::<i32>().unwrap());
                }
                "framerate" => {
                    // Get locks on the internals
                    let mut clock_internals = self.clock_internals.write().unwrap();

                    // Update `framerate`
                    clock_internals.framerate = value.get_some::<gst::Fraction>().unwrap();

                    // Update `frameset_duration` and `deadline_duration`
                    let settings = self.settings.read().unwrap();

                    let (num, den): (i32, i32) = clock_internals.framerate.into();

                    let duration_sec = match den as f32 / num as f32 {
                        x if x.is_normal() => x,
                        _ => 1f32 / DEFAULT_FRAMERATE as f32,
                    };                    

                    clock_internals.update_durations(duration_sec, settings.deadline_multiplier)
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
    /// * `sink_pad_names` - The vector containing all sink pad names.
    fn get_current_downstream_caps(
        &self,
        element: &gst::Element,
        sink_pad_names: &[String],
    ) -> gst::Caps {
        // Join all the pad names to create the 'streams' section of the CAPS
        let streams = sink_pad_names
            .iter()
            .map(|s| &s[5..])
            .collect::<Vec<&str>>()
            .join(",");

        let mut downstream_caps = gst::Caps::new_simple(
            "video/rgbd",
            &[
                ("streams", &streams),
                ("framerate", &self.clock_internals.read().unwrap().framerate),
            ],
        );

        let mut_caps = downstream_caps
            .make_mut()
            .get_mut_structure(0)
            .expect("rgbdmux: Could not get mutable CAPS");

        // Map the caps into their corresponding stream formats
        for pad_name in sink_pad_names.iter() {
            // First find the current CAPS of Pad we're currently dealing with
            let pad_caps = element
                .get_static_pad(pad_name)
                .unwrap_or_else(|| {
                    panic!(
                        "Could not get static pad from aggregator with name `{}`",
                        pad_name
                    )
                })
                .get_current_caps();
            if let Some(pc) = pad_caps {
                self.elementary_caps_to_rgbd(&pc, pad_name, mut_caps)
            }
        }

        gst_info!(
            CAT,
            obj: element,
            "stream_caps were found to be: {:?}.",
            downstream_caps
        );

        downstream_caps.to_owned()
    }

    /// Query downstream element of `aggregator` for CAPS and extracts format fields for each stream.
    /// # Arguments
    /// * `aggregator` - The aggregator that represents `rgbdmux`.
    /// # Returns
    /// * `HashMap<String, String>` - Hashmap containing <stream, format>.
    fn query_downstream_video_formats(
        &self,
        aggregator: &gst_base::Aggregator,
    ) -> HashMap<String, String> {
        let src_pad = aggregator
            .get_static_pad("src")
            .expect("rgbdmux: Element must have a src pad to receive a src_query");
        let src_pad_template_caps = aggregator
            .get_pad_template("src")
            .expect("rgbdmux: Could not find src-pad template")
            .get_caps();

        // Create CAPS query with filter based on template CAPS
        let mut request_downstream_caps_query =
            gst::query::Caps::new(src_pad_template_caps.as_ref());

        // Send the query and receive sink CAPS of the downstream element
        if !src_pad.peer_query(&mut request_downstream_caps_query) {
            gst_debug!(
                CAT,
                obj: aggregator,
                "Cannot send CAPS query downstream. The src pad of this element is probably not yet linked.",
            );
            return HashMap::new();
        }

        if let Some(requested_caps) = request_downstream_caps_query.get_result() {
            // We can only handle fixed CAPS here
            if !requested_caps.is_fixed() {
                gst_warning!(
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
                    Some((
                        field.replace("_format", ""),
                        value.get::<String>().unwrap().unwrap_or_default(),
                    ))
                }
            })
            .collect::<HashMap<String, String>>()
    }
}

impl ObjectImpl for RgbdMux {
    glib_object_impl!();

    fn set_property(&self, _obj: &glib::Object, id: usize, value: &glib::Value) {
        let mut settings = self.settings.write().unwrap();

        match PROPERTIES[id] {
            subclass::Property(prop @ "drop-to-synchronise", ..) => {
                let drop_to_synchronise =
                    get_property_and_debug(*CAT, value, prop, settings.drop_to_synchronise);
                settings.drop_to_synchronise = drop_to_synchronise;
            }
            subclass::Property(prop @ "drop-if-missing", ..) => {
                let drop_if_missing =
                    get_property_and_debug(*CAT, value, prop, settings.drop_if_missing);
                settings.drop_if_missing = drop_if_missing;
            }
            subclass::Property(prop @ "deadline-multiplier", ..) => {
                let deadline_multiplier =
                    get_property_and_debug(*CAT, value, prop, settings.deadline_multiplier);
                settings.deadline_multiplier = deadline_multiplier;
            }
            subclass::Property(prop @ "send-gap-events", ..) => {
                let send_gap_events =
                    get_property_and_debug(*CAT, value, prop, settings.send_gap_events);
                settings.send_gap_events = send_gap_events;
            }
            _ => unimplemented!("Property is not implemented"),
        };
    }

    fn get_property(&self, _obj: &glib::Object, id: usize) -> Result<glib::Value, ()> {
        let settings = self.settings.read().unwrap();

        match PROPERTIES[id] {
            subclass::Property("drop-to-synchronise", ..) => {
                Ok(settings.drop_to_synchronise.to_value())
            }
            subclass::Property("drop-if-missing", ..) => Ok(settings.drop_if_missing.to_value()),
            subclass::Property("deadline-multiplier", ..) => {
                Ok(settings.deadline_multiplier.to_value())
            }
            subclass::Property("send-gap-events", ..) => Ok(settings.send_gap_events.to_value()),
            _ => unimplemented!("Property is not implemented"),
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
