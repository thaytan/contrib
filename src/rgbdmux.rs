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
use std::error::Error;
use std::fmt;
use std::fmt::{Display, Formatter};
use std::sync::{Mutex, RwLock};

lazy_static! {
    static ref CAT: gst::DebugCategory = gst::DebugCategory::new(
        "rgbdmux",
        gst::DebugColorFlags::empty(),
        Some("RGB-D Muxer"),
    );
}

/// A flag that determines what to do if one of the sink pads does not
/// receive a buffer within the aggregation deadline. If set to true,
/// all other buffers will be dropped.
const DEFAULT_DROP_ALL_BUFFERS_IF_ONE_IS_MISSING: bool = true;
/// A flag that determines what to do if the timestamps (pts) of the
/// received buffers differ. If set to true, the buffers that are
/// behind, i.e. those that have the smallest pts, get dropped.
const DEFAULT_DROP_BUFFERS_TO_SYNCHRONISE_STREAMS: bool = true;
/// Default deadline multiplier for the deadline based aggregation
const DEFAULT_DEADLINE_MULTIPLIER: f32 = 1.25;
/// A flag that determines whether to send gap events if buffers are
/// explicitly dropped
const DEFAULT_SEND_GAP_EVENTS: bool = false;
/// Default framerate of the streams
const DEFAULT_FRAMERATE: i32 = 30;

static PROPERTIES: [subclass::Property; 4] = [
    subclass::Property("drop-if-missing", |name| {
        glib::ParamSpec::boolean(
            name,
            "Drop all buffers in one is missing",
            "If enabled, deadline based aggregation is employed with the `deadline-multiplier` property determining the duration of the deadline. If enabled and one of the sink pads does not receive a buffer within the aggregation deadline, all other buffers are dropped.",
            DEFAULT_DROP_ALL_BUFFERS_IF_ONE_IS_MISSING,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("deadline-multiplier", |name| {
        glib::ParamSpec::float(
            name,
            "Deadline multiplier",
            "Determines the duration of the deadline for the deadline based aggregation. The deadline duration is inversely proportional to the framerate and `deadline-multiplier` is applied as `deadline-multiplier`/`framerate`. Applicable only if `drop-if-missing` is enabled.",
            std::f32::MIN_POSITIVE,
            std::f32::MAX,
            DEFAULT_DEADLINE_MULTIPLIER,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("drop-to-synchronise", |name| {
        glib::ParamSpec::boolean(
            name,
            "Drop buffers to synchronise streams",
            "Determines what to do if the timestamps (pts) of the received buffers differ. If set to true, the buffers that are behind, i.e. those that have the smallest pts, get dropped.",
            DEFAULT_DROP_BUFFERS_TO_SYNCHRONISE_STREAMS,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("send-gap-events", |name| {
        glib::ParamSpec::boolean(
            name,
            "Send gap events downstream",
            "Determines whether to send gap events downstream if buffers are explicitly dropped.",
            DEFAULT_SEND_GAP_EVENTS,
            glib::ParamFlags::READWRITE,
        )
    }),
];

#[derive(Debug, Clone)]
/// Custom error of `rgbdmux` element
struct MuxingError(&'static str);
impl Error for MuxingError {}
impl Display for MuxingError {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "RGBD muxing error: {}", self.0)
    }
}
/// Conversion from `gst::ErrorMessage` to MuxingError.
impl From<gst::ErrorMessage> for MuxingError {
    fn from(error: gst::ErrorMessage) -> MuxingError {
        MuxingError(std::boxed::Box::leak(format!("{}", error).into_boxed_str()))
    }
}

/// A struct representation of the `rgbdmux` element
struct RgbdMux {
    /// List of sink pad names utilised for easy access under a Mutex
    sink_pads: Mutex<Vec<String>>,
    /// Settings based on properties of the element that are under a Mutex
    settings: RwLock<Settings>,
    /// Mutex protecting the clock internals of the element
    clock_internals: Mutex<RgbdMuxClockInternals>,
    /// Contains stream formats that are requested by the downstream element as a HashMap<stream, format> under a Mutex
    requested_stream_formats: Mutex<HashMap<String, String>>,
}

/// Internals of the element related to clock that are under Mutex.
struct RgbdMuxClockInternals {
    /// Framerate of the streams
    framerate: gst::Fraction,
    /// The previous timestamps (pts) of the buffers
    previous_timestamp: gst::ClockTime,
    /// Timestamp that is used to keep track of recurring GAP events
    gap_timestamp: gst::ClockTime,
    /// The duration of one frameset
    frameset_duration: gst::ClockTime,
}

/// A struct containing properties that are under mutex
struct Settings {
    drop_if_missing: bool,
    deadline_multiplier: f32,
    drop_to_synchronise: bool,
    send_gap_events: bool,
}

impl ObjectSubclass for RgbdMux {
    const NAME: &'static str = "rgbdmux";
    type ParentType = gst_base::Aggregator;
    type Instance = gst::subclass::ElementInstanceStruct<Self>;
    type Class = subclass::simple::ClassStruct<Self>;

    glib_object_subclass!();

    fn new() -> Self {
        Self {
            sink_pads: Mutex::new(Vec::new()),
            settings: RwLock::new(Settings {
                drop_if_missing: DEFAULT_DROP_ALL_BUFFERS_IF_ONE_IS_MISSING,
                deadline_multiplier: DEFAULT_DEADLINE_MULTIPLIER,
                drop_to_synchronise: DEFAULT_DROP_BUFFERS_TO_SYNCHRONISE_STREAMS,
                send_gap_events: DEFAULT_SEND_GAP_EVENTS,
            }),
            clock_internals: Mutex::new(RgbdMuxClockInternals {
                framerate: gst::Fraction::new(DEFAULT_FRAMERATE, 1),
                previous_timestamp: gst::CLOCK_TIME_NONE,
                gap_timestamp: gst::CLOCK_TIME_NONE,
                frameset_duration: gst::CLOCK_TIME_NONE,
            }),
            requested_stream_formats: Mutex::new(HashMap::new()),
        }
    }

    fn class_init(klass: &mut subclass::simple::ClassStruct<Self>) {
        klass.set_metadata(
            "RGB-D Muxer",
            "Muxer/RGB-D",
            "Muxes multiple `video/x-raw` into a single `video/rgbd`",
            "Andrej Orsula <andrej.orsula@aivero.com>, Tobias Morell <tobias.morell@aivero.com>",
        );

        klass.install_properties(&PROPERTIES);

        // sink pads
        let mut sink_caps = gst::Caps::new_simple("video/x-raw", &[]);
        {
            let sink_caps = sink_caps
                .get_mut()
                .expect("Could not get mutable reference to sink_caps");
            sink_caps.append(gst::Caps::new_simple("meta/x-klv", &[("parsed", &true)]));
            sink_caps.append(gst::Caps::new_simple("image/jpeg", &[]));
        }

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

    fn set_property(&self, obj: &glib::Object, id: usize, value: &glib::Value) {
        let element = obj
            .downcast_ref::<gst_base::Aggregator>()
            .expect("Could not cast `rgbdmux` to Aggregator");
        let mut settings = self.settings.write().unwrap();

        let property = &PROPERTIES[id];
        match *property {
            subclass::Property("drop-if-missing", ..) => {
                let drop_if_missing = value.get_some().unwrap_or_else(|err| panic!("rgbdmux: Failed to set property `drop_if_missing` due to incorrect type: {:?}", err));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `drop-if-missing` from {} to {}",
                    settings.drop_if_missing,
                    drop_if_missing
                );
                settings.drop_if_missing = drop_if_missing;
            }
            subclass::Property("deadline-multiplier", ..) => {
                let deadline_multiplier = value.get_some().unwrap_or_else(|err| panic!("rgbdmux: Failed to set property `deadline-multiplier` due to incorrect type: {:?}", err));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `deadline-multiplier` from {} to {}",
                    settings.deadline_multiplier,
                    deadline_multiplier
                );
                settings.deadline_multiplier = deadline_multiplier;
            }
            subclass::Property("drop-to-synchronise", ..) => {
                let drop_to_synchronise = value.get_some().unwrap_or_else(|err| panic!("rgbdmux: Failed to set property `drop-to-synchronise` due to incorrect type: {:?}", err));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `drop-to-synchronise` from {} to {}",
                    settings.drop_to_synchronise,
                    drop_to_synchronise
                );
                settings.drop_to_synchronise = drop_to_synchronise;
            }
            subclass::Property("send-gap-events", ..) => {
                let send_gap_events = value.get_some().unwrap_or_else(|err| panic!("rgbdmux: Failed to set property `send-gap-events` due to incorrect type: {:?}", err));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `send-gap-events` from {} to {}",
                    settings.send_gap_events,
                    send_gap_events
                );
                settings.send_gap_events = send_gap_events;
            }
            _ => unimplemented!("Property is not implemented"),
        };
    }

    fn get_property(&self, _obj: &glib::Object, id: usize) -> Result<glib::Value, ()> {
        let settings = &self.settings.read().map_err(|e| {
            gst_error!(CAT, "Settings could not be locked: {:?}", e);
        })?;

        let prop = &PROPERTIES[id];
        match *prop {
            subclass::Property("drop-if-missing", ..) => Ok(settings.drop_if_missing.to_value()),
            subclass::Property("deadline-multiplier", ..) => {
                Ok(settings.deadline_multiplier.to_value())
            }
            subclass::Property("drop-to-synchronise", ..) => {
                Ok(settings.drop_to_synchronise.to_value())
            }
            subclass::Property("send-gap-events", ..) => Ok(settings.send_gap_events.to_value()),
            _ => unimplemented!("Property is not implemented"),
        }
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
            .unwrap_or_else(|_| panic!("Could not deactivate a sink-pad: {:?}", pad));

        // Remove the pad from the element
        element
            .remove_pad(pad)
            .unwrap_or_else(|_| panic!("Could not remove a sink-pad: {:?}", pad));

        // Remove the pad from our internal reference HashMap
        let pad_name = pad.get_name().as_str().to_string();
        gst_debug!(CAT, obj: element, "release_pad: {}", pad_name);
        {
            self.sink_pads
                .lock()
                .expect("Could not lock sink pads")
                .retain(|x| *x != pad_name);
        }

        // Renegotiate only if the element is not shutting down due to EOS
        let (state_result, _state_current, state_pending) = element.get_state(gst::CLOCK_TIME_NONE);
        if state_result.is_ok() && state_pending != gst::State::VoidPending {
            self.renegotiate_downstream_caps(element);
        }
    }
}

impl AggregatorImpl for RgbdMux {
    fn aggregate(
        &self,
        aggregator: &gst_base::Aggregator,
        _timeout: bool,
    ) -> Result<gst::FlowSuccess, gst::FlowError> {
        // Lock the settings
        let settings = &self.settings.read().expect("Could not lock settings");
        // Get the list of available names
        let sink_pad_names = &self.sink_pads.lock().expect("Could not lock sink pads");

        if settings.drop_if_missing {
            // Check all sink pads for queued buffers. If one pad has no queued buffer, drop all other buffers.
            self.drop_buffers_if_one_missing(aggregator, sink_pad_names, settings.send_gap_events)
                .map_err(|_| gst::FlowError::CustomError)?;
        }

        if settings.drop_to_synchronise {
            // Make sure the streams are synchronised
            self.check_synchronisation(aggregator, sink_pad_names, settings.send_gap_events)
                .map_err(|_| gst::FlowError::CustomError)?;
        }

        // Mux all buffers to a single output buffer.
        let output_buffer = self.mux_buffers(aggregator, sink_pad_names);

        gst_debug!(CAT, obj: aggregator, "A frameset was muxed.");

        // Finish the buffer if all went fine
        self.finish_buffer(aggregator, output_buffer)
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
        let name = req_name?;
        if !name.starts_with("sink_") {
            return None;
        }

        let sink_pads = &mut self.sink_pads.lock().expect("Could not lock sink pads");
        gst_debug!(CAT, obj: aggregator, "create_new_pad for name: {}", name);
        // Create new sink pad from the template
        let new_sink_pad = gst::Pad::new_from_template(
            &self.get_sink_pad_template_with_modified_format(aggregator, name),
            Some(name),
        )
        .downcast::<gst_base::AggregatorPad>()
        .expect("Could not cast pad to AggregatorPad");

        // Drop all buffers on already existing pads (if any)
        self.drop_all_queued_buffers(aggregator, sink_pads);

        // Insert the new sink pad name into the struct
        sink_pads.push(name.to_string());

        // Activate the sink pad
        new_sink_pad
            .set_active(true)
            .expect("Failed to activate `rgbdmux` sink pad");

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
        gst_debug!(CAT, "update_src_caps");
        // if no sink pads are present, we're not ready to negotiate CAPS, otherwise do the negotiation
        if self.sink_pads.lock().unwrap().is_empty() {
            Err(gst_base::AGGREGATOR_FLOW_NEED_DATA) // we're not ready to decide on CAPS yet
        } else {
            Ok(self.get_current_downstream_caps(aggregator.upcast_ref::<gst::Element>()))
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
        gst_debug!(CAT, obj: elm, "fixate_src_caps");
        self.get_current_downstream_caps(elm)
    }

    /// Called when the element needs to know the running time of the next rendered buffer for live pipelines.
    /// This causes deadline based aggregation to occur. Returning GST_CLOCK_TIME_NONE causes the element to
    /// wait for buffers on all sink pads before aggregating.
    /// # Arguments
    /// * `_aggregator` - A reference to the element that represents `rgbdmux` in GStreamer.
    fn get_next_time(&self, _aggregator: &gst_base::Aggregator) -> gst::ClockTime {
        if self
            .settings
            .read()
            .expect("Could not lock settings")
            .drop_if_missing
        {
            // If `drop-if-missing` is enabled, a deadline for the aggregation is returned.
            let clock_internals = &self
                .clock_internals
                .lock()
                .expect("Could not lock clock internals");
            clock_internals.previous_timestamp + clock_internals.frameset_duration
        } else {
            // Else, the aggregation has no deadline.
            gst::CLOCK_TIME_NONE
        }
    }

    /// Called whenever a query is received at the src pad.
    /// CAPS query is used to obtain requests for formats of the individual video streams.
    /// # Arguments
    /// * `aggregator` - The element that represents the `rgbdmux` in GStreamer.
    /// * `query` - The query that should be handled.
    fn src_query(&self, aggregator: &gst_base::Aggregator, query: &mut gst::QueryRef) -> bool {
        #[allow(clippy::single_match)]
        match query.view_mut() {
            // Wait until CAPS query is received on the src pad
            gst::QueryView::Caps(_query_caps) => {
                // Get the src_pad used for sending the query to the linked downstream element
                let src_pad = aggregator
                    .get_static_pad("src")
                    .expect("Element must have a src pad to receive a src_query");
                // Get the default CAPS from the src pad template
                let src_pad_template_caps = aggregator
                    .get_pad_template("src")
                    .expect("Could not find src-pad template")
                    .get_caps();
                // Create CAPS query
                let mut request_downstream_caps_query =
                    gst::Query::new_caps(src_pad_template_caps.as_ref());

                // Send the query and receive the sink CAPS of the downstream element
                if src_pad.peer_query(&mut request_downstream_caps_query) {
                    if let Some(requested_caps) = request_downstream_caps_query.get_result() {
                        // Before extraction, intersect with src pad template caps
                        let requested_caps = requested_caps.intersect(
                            &src_pad_template_caps
                                .expect("Rgbdmux defines a src pad template with caps"),
                        );
                        // Extract formats from these caps for use when creating new CAPS
                        let requested_stream_formats = &mut *self
                            .requested_stream_formats
                            .lock()
                            .expect("Could not lock reqested_stream_formats");
                        *requested_stream_formats =
                            self.extract_formats_from_rgbd_caps(&requested_caps);
                    }
                }
            }
            _ => {}
        }

        // Let parent handle all queries
        self.parent_src_query(aggregator, query)
    }

    fn sink_event(
        &self,
        aggregator: &gst_base::Aggregator,
        aggregator_pad: &gst_base::AggregatorPad,
        event: gst::Event,
    ) -> bool {
        match event.view() {
            gst::EventView::Eos(_) => {
                // Simply forward the EOS event to the src pad
                let src_pad = aggregator
                    .get_static_pad("src")
                    .expect("Aggregator element must have a src pad");
                src_pad.push_event(event)
            }
            // Let parent handle all other events
            _ => self.parent_sink_event(aggregator, aggregator_pad, event),
        }
    }
}

impl RgbdMux {
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
            .expect("Could not downcast pad to AggregatorPad")
    }

    /// Get a buffer from the pad with the given `pad_name` on the given `aggregator`. This function
    /// also tags the buffer with a correct title tag.
    /// # Arguments
    /// * `aggregator` - The aggregator that holds a pad with the given name.
    /// * `pad_name` - The name of the pad to read a buffer from.
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
        if let Some(buffer_mut) = buffer.get_mut() {
            // Get the stream name by truncating the "sink_" prefix
            let stream_name = &pad_name[5..];

            // Tag the buffer
            rgbd::tag_buffer(buffer_mut, stream_name)?;
        } else {
            gst_warning!(
                CAT,
                obj: aggregator,
                "Could not tag a buffer from pad: {}",
                pad_name
            );
        }

        // Return the tagged buffer
        Ok(buffer)
    }

    /// Check all sink pads for queued buffers. If one pad has no queued buffer, drop all other buffers and return error.
    /// # Arguments
    /// * `aggregator` - The aggregator to consider.
    /// * `sink_pad_names` - The vector containing all sink pad names.
    /// * `send_gap_events` - Flag that determines whether to send GAP events when dropping buffers.
    fn drop_buffers_if_one_missing(
        &self,
        aggregator: &gst_base::Aggregator,
        sink_pad_names: &[String],
        send_gap_events: bool,
    ) -> Result<(), MuxingError> {
        // Iterate over all sink pads
        for sink_pad_name in sink_pad_names.iter() {
            // Get the sink pad given its name
            let sink_pad = Self::get_aggregator_pad(aggregator, sink_pad_name);

            // Check whether the aggregator pad has a buffer available
            if !sink_pad.has_buffer() {
                gst_warning!(
                    CAT,
                    obj: aggregator,
                    "No buffer is queued on `{}` pad. Dropping all other buffers.",
                    sink_pad_name
                );

                // Send gap event downstream
                if send_gap_events {
                    self.send_gap_event(aggregator);
                }

                // Drop all buffers
                self.drop_all_queued_buffers(aggregator, sink_pad_names);

                // Return Err
                return Err(MuxingError(
                    "One of the pads did not have a queued buffer. Dropped all other buffers.",
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
    fn drop_all_queued_buffers(
        &self,
        aggregator: &gst_base::Aggregator,
        sink_pad_names: &[String],
    ) {
        // Update the current timestamp to CLOCK_TIME_NONE, i.e no deadline
        self.clock_internals
            .lock()
            .expect("Could not lock clock internals")
            .previous_timestamp = gst::CLOCK_TIME_NONE;

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
    /// * `send_gap_events` - Flag that determines whether to send GAP events when dropping buffers.
    /// # Returns
    /// * `Err(MuxingError)` - if frames
    fn check_synchronisation(
        &self,
        aggregator: &gst_base::Aggregator,
        sink_pad_names: &[String],
        send_gap_events: bool,
    ) -> Result<(), MuxingError> {
        // Get timestamps of buffers queued on the sink pads
        let timestamps: Vec<(String, gst::ClockTime)> =
            self.get_timestamps(aggregator, sink_pad_names);

        // Get the min and max timestamps of the queued buffers
        let min_pts = &timestamps.iter().map(|(_, pts)| pts).min().unwrap();
        let max_pts = &timestamps.iter().map(|(_, pts)| pts).max().unwrap();

        // If all timestamps are the same, the streams are already synchronised
        if min_pts == max_pts {
            return Ok(());
        }

        // Send gap event downstream
        if send_gap_events {
            self.send_gap_event(aggregator);
        }

        // If the streams are not synchronised, iterature over all buffers and
        // drop those that are late
        for (sink_pad_name, timestamp) in timestamps.iter() {
            if timestamp < max_pts {
                // Get sink pad with the given name
                let sink_pad = Self::get_aggregator_pad(aggregator, sink_pad_name);
                // Drop the buffer
                sink_pad.drop_buffer();
            }
        }

        // Update the current timestamp to CLOCK_TIME_NONE, i.e no deadline
        self.clock_internals
            .lock()
            .expect("Could not lock clock internals")
            .previous_timestamp = gst::CLOCK_TIME_NONE;

        gst_warning!(
            CAT,
            obj: aggregator,
            "Dropped buffers to synchronise the streams"
        );

        // Return error
        Err(MuxingError("Dropped buffers to synchronise the streams"))
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
        // If there is no buffer, leave the main buffer empty
        let mut main_buffer = Self::get_tagged_buffer(aggregator, &sink_pad_names[0])
            .unwrap_or_else(|_e| {
                gst_warning!(
                    CAT,
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

        // Update the current timestamp
        let clock_internals = &mut self
            .clock_internals
            .lock()
            .expect("Could not lock clock internals");
        clock_internals.previous_timestamp = main_buffer_mut_ref.get_pts();
        // Reset GAP event timestamp on successful aggregation
        clock_internals.gap_timestamp = gst::CLOCK_TIME_NONE;

        // Iterate over all other sink pads, excluding the first one
        for sink_pad_name in sink_pad_names.iter().skip(1) {
            // Get a buffer that was queue on the sink pad and tag it with a title
            match Self::get_tagged_buffer(aggregator, sink_pad_name) {
                Ok(mut buffer) => {
                    // Attach to the main bufer
                    BufferMeta::add(main_buffer_mut_ref, &mut buffer);
                }
                Err(_) => {
                    gst_warning!(
                        CAT,
                        obj: aggregator,
                        "No buffer is queued on `{}` pad. No corresponding buffer will be attached to the main buffer.",
                        sink_pad_name
                    );
                }
            }
        }
        // Return the main buffer
        main_buffer
    }

    /// Sends a gap event downstream.
    /// # Arguments
    /// * `aggregator` - The aggregator to drop all queued buffers for.
    fn send_gap_event(&self, aggregator: &gst_base::Aggregator) {
        let clock_internals = &mut self
            .clock_internals
            .lock()
            .expect("Could not lock clock internals");

        // If not set, make gap_timestamp based on the previous valid timestamp
        if clock_internals.gap_timestamp == gst::CLOCK_TIME_NONE {
            // Make sure the previous timestamp is valid first
            if clock_internals.previous_timestamp == gst::CLOCK_TIME_NONE {
                return;
            }
            clock_internals.gap_timestamp = clock_internals.previous_timestamp;
        }

        // Add frameset duration to offset the timestamp to the next frameset
        clock_internals.gap_timestamp =
            clock_internals.gap_timestamp + clock_internals.frameset_duration;

        // Create and send the GAP event
        let gap_event = gst::Event::new_gap(
            clock_internals.gap_timestamp,
            clock_internals.frameset_duration,
        )
        .build();
        if !aggregator.send_event(gap_event) {
            gst_error!(CAT, obj: aggregator, "Failed to send gap event");
        }
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
                    let clock_internals = &mut self
                        .clock_internals
                        .lock()
                        .expect("Could not lock clock internals");
                    let settings = &self.settings.read().expect("Could not lock settings");

                    // Update `framerate`
                    clock_internals.framerate = value.get_some::<gst::Fraction>().unwrap();

                    // If deadline based aggregation is selected, update the `frameset_duration`
                    clock_internals.frameset_duration = if settings.drop_if_missing {
                        // HERE
                        //
                        //
                        //
                        // Update also the `frameset_duration` based on `framerate` and
                        // `deadline-multiplier` property
                        let (num, den): (i32, i32) = clock_internals.framerate.into();
                        let frame_duration = std::time::Duration::from_secs_f32(
                            settings.deadline_multiplier * (den as f32 / num as f32),
                        );
                        gst::ClockTime::from_nseconds(frame_duration.as_nanos() as u64)
                    } else {
                        gst::CLOCK_TIME_NONE
                    }
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
    /// # Important
    /// Requires self.sink_pads to be unlocked.
    fn get_current_downstream_caps(&self, element: &gst::Element) -> gst::Caps {
        // First lock sink_pads, so that we may iterate it
        let sink_pads = &self.sink_pads.lock().expect("Could not lock sink pads");

        // Join all the pad names to create the 'streams' section of the CAPS
        let streams = sink_pads
            .iter()
            .map(|s| &s[5..])
            .collect::<Vec<&str>>()
            .join(",");

        let mut downstream_caps = gst::Caps::new_simple(
            "video/rgbd",
            &[
                ("streams", &streams),
                (
                    "framerate",
                    &self
                        .clock_internals
                        .lock()
                        .expect("Could not lock clock internals")
                        .framerate,
                ),
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
                .unwrap_or_else(|| {
                    panic!(
                        "Could not get static pad from aggregator with name `{}`",
                        pad_name
                    )
                })
                .get_current_caps();
            if let Some(pc) = pad_caps {
                self.push_sink_caps_format(&pc, pad_name, mut_caps)
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

    /// Generates and sends new CAPS for the downstream elements. This function automatically
    /// generates CAPS based on the sink_pads of the muxer and their current CAPS.
    /// # Arguments
    /// * `element` - The element that represents the `rgbdmux`.
    fn renegotiate_downstream_caps(&self, element: &gst::Element) {
        gst_debug!(CAT, obj: element, "renegotiate_downstream_caps");
        // Figure out the new caps the element should output
        let ds_caps = self.get_current_downstream_caps(element);
        // And send a CAPS event downstream
        let caps_event = gst::Event::new_caps(&ds_caps).build();
        if !element.send_event(caps_event) {
            gst_error!(CAT, obj: element, "Failed to send CAPS negotiation event");
        }
    }

    /// Extracts format field for each stream in `video/rgbd` CAPS.
    /// # Arguments
    /// * `caps` - Formats are extracted from these `video/rgbd` CAPS.
    /// # Returns
    /// * `HashMap<String, String>` - Hashmap containing <stream, format>.
    fn extract_formats_from_rgbd_caps(&self, caps: &gst::Caps) -> HashMap<String, String> {
        // Iterate over all fields in the input CAPS and retain only the format field
        caps.iter()
            .next()
            .expect("Downstream element of rgbdmux has not CAPS")
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

    /// Determines what pad template to use for a new sink pad. It attaches a format to the CAPS if
    /// downstream element has such request.
    /// If there is no such request, the default sink pad template is returned.
    /// # Arguments
    /// * `aggregator` - The element that represents the `rgbdmux` in GStreamer.
    /// * `pad_name` - Name of the new sink pad.
    /// # Returns
    /// * `gstreamer::PadTemplate` to use for the creation of the new sink pad.
    fn get_sink_pad_template_with_modified_format(
        &self,
        aggregator: &gst_base::Aggregator,
        pad_name: &str,
    ) -> gstreamer::PadTemplate {
        // Lock the stream formats requested by downstream element
        let requested_stream_formats = &mut *self
            .requested_stream_formats
            .lock()
            .expect("Could not lock reqested_stream_formats");

        // Get the default sink pad template
        let default_sink_pad_template = aggregator
            .get_pad_template("sink_%s")
            .expect("Could not find sink-pad template");

        // Iterate over all requested formats and find the matching stream
        for (stream_name, format) in requested_stream_formats.iter() {
            // Match the current request
            if pad_name == format!("sink_{}", stream_name) {
                // Create editable version of the default CAPS (since pad template cannot be directly edited)
                let mut caps = default_sink_pad_template.get_caps().unwrap();
                {
                    let caps = caps
                        .make_mut()
                        .get_mut_structure(0)
                        .expect("Could not get mutable CAPS in rgbdmux");

                    // Add the format to the CAPS
                    caps.set("format", &format);
                }

                // Return the pad template that was adjusted with new CAPS
                return gst::PadTemplate::new_with_gtype(
                    "sink_%s",
                    default_sink_pad_template.get_property_direction(),
                    default_sink_pad_template.get_property_presence(),
                    &caps,
                    default_sink_pad_template.get_property_gtype(),
                )
                .unwrap_or_else(|_| {
                    panic!("Could not create a custom template for {} pad", pad_name)
                });
            }
        }

        // If no specific format was requested for the stream by the downstream element, return the default sink pad template
        default_sink_pad_template
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
