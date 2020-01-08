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

use std::sync::Mutex;

use glib::subclass;
use gst::subclass::prelude::*;
use gst_base::prelude::*;
use gst_base::subclass::prelude::*;

use gst_depth_meta::buffer::BufferMeta;
use gst_depth_meta::tags::TagsMeta;
use rs2;
use rs2::high_level_utils::StreamInfo;

use crate::errors::*;
use crate::properties::*;
use crate::realsense_timestamp_mode::RealsenseTimestampMode;
use crate::rs_meta::rs_meta_serialization::*;
use crate::settings::*;

/// A struct representation of the `realsensesrc` element
struct RealsenseSrc {
    cat: gst::DebugCategory,
    internals: Mutex<RealsenseSrcInternals>,
}

/// Internals of the element that are under Mutex
struct RealsenseSrcInternals {
    settings: Settings,
    state: State,
    base_time: std::time::Duration,
}

/// An enum containing the current state of the RealSense pipeline
enum State {
    Stopped,
    Started { pipeline: rs2::pipeline::Pipeline },
}

impl ObjectSubclass for RealsenseSrc {
    const NAME: &'static str = "realsensesrc";
    type ParentType = gst_base::BaseSrc;
    type Instance = gst::subclass::ElementInstanceStruct<Self>;
    type Class = subclass::simple::ClassStruct<Self>;

    glib_object_subclass!();

    fn class_init(klass: &mut subclass::simple::ClassStruct<Self>) {
        klass.set_metadata(
            "Realsense Source",
            "Source/RGB-D/Realsense",
            "Stream `video/rgbd` from a RealSense device",
            "Niclas Moeslund Overby <niclas.overby@aivero.com>, Andrej Orsula <andrej.orsula@aivero.com>, Tobias Morell <tobias.morell@aivero.com>",
        );

        klass.install_properties(&PROPERTIES);

        // Create src pad template with `video/rgbd` caps
        let src_caps = gst::Caps::new_simple(
            "video/rgbd",
            &[
                // List of available streams meant for indicating their respective priority
                (
                    "streams",
                    &"depth,infra1,infra2,color,depthmeta,infra1meta,infra2meta,colormeta",
                ),
                (
                    "framerate",
                    &gst::FractionRange::new(
                        gst::Fraction::new(MIN_FRAMERATE, 1),
                        gst::Fraction::new(MAX_FRAMERATE, 1),
                    ),
                ),
            ],
        );
        klass.add_pad_template(
            gst::PadTemplate::new(
                "src",
                gst::PadDirection::Src,
                gst::PadPresence::Always,
                &src_caps,
            )
            .expect("Could not add src pad template in realsensesrc"),
        );
    }

    fn new() -> Self {
        Self {
            cat: gst::DebugCategory::new(
                "realsensesrc",
                gst::DebugColorFlags::empty(),
                Some("Realsense Source"),
            ),
            internals: Mutex::new(RealsenseSrcInternals {
                settings: Settings::default(),
                state: State::Stopped,
                base_time: std::time::Duration::new(0, 0),
            }),
        }
    }
}

impl ObjectImpl for RealsenseSrc {
    glib_object_impl!();

    fn set_property(&self, obj: &glib::Object, id: usize, value: &glib::Value) {
        let element = obj
            .downcast_ref::<gst_base::BaseSrc>()
            .expect("Could not cast realsensesrc to BaseSrc");
        let settings = &mut self
            .internals
            .lock()
            .expect("Could not obtain lock internals mutex")
            .settings;

        let property = &PROPERTIES[id];
        match *property {
            subclass::Property("serial", ..) => {
                let serial = value.get::<String>();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `serial` from {:?} to {:?}",
                    settings.serial,
                    serial
                );
                settings.serial = serial;
                obj.downcast_ref::<gst_base::BaseSrc>()
                    .unwrap()
                    .set_live(true);
            }
            subclass::Property("rosbag-location", ..) => {
                let rosbag_location = value.get::<String>();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `rosbag-location` from {:?} to {:?}",
                    settings.rosbag_location,
                    rosbag_location
                );
                settings.rosbag_location = rosbag_location;
                obj.downcast_ref::<gst_base::BaseSrc>()
                    .unwrap()
                    .set_live(false);
            }
            subclass::Property("json-location", ..) => {
                let json_location = value.get::<String>();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `json-location` from {:?} to {:?}",
                    settings.json_location,
                    json_location
                );
                settings.json_location = json_location;
            }
            subclass::Property("enable-depth", ..) => {
                let enable_depth = value.get().expect(&format!("Failed to set property `enable-depth` on realsensesrc. Expected a boolean, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `enable-depth` from {} to {}",
                    settings.streams.enabled_streams.depth,
                    enable_depth
                );
                settings.streams.enabled_streams.depth = enable_depth;
            }
            subclass::Property("enable-infra1", ..) => {
                let enable_infra1 = value.get().expect(&format!("Failed to set property `enable-infra` on realsensesrc. Expected a boolean, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `enable-infra1` from {} to {}",
                    settings.streams.enabled_streams.infra1,
                    enable_infra1
                );
                settings.streams.enabled_streams.infra1 = enable_infra1;
            }
            subclass::Property("enable-infra2", ..) => {
                let enable_infra2 = value.get().expect(&format!("Failed to set property `enable-infra2` on realsensesrc. Expected a boolean, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `enable-infra2` from {} to {}",
                    settings.streams.enabled_streams.infra2,
                    enable_infra2
                );
                settings.streams.enabled_streams.infra2 = enable_infra2;
            }
            subclass::Property("enable-color", ..) => {
                let enable_color = value.get().expect(&format!("Failed to set property `enable-color` on realsensesrc. Expected a boolean, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `enable-color` from {} to {}",
                    settings.streams.enabled_streams.color,
                    enable_color
                );
                settings.streams.enabled_streams.color = enable_color;
            }
            subclass::Property("depth-width", ..) => {
                let depth_width = value.get().expect(&format!("Failed to set property `depth-width` on realsensesrc. Expected an int, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `depth-width` from {} to {}",
                    settings.streams.depth_resolution.width,
                    depth_width
                );
                settings.streams.depth_resolution.width = depth_width;
            }
            subclass::Property("depth-height", ..) => {
                let depth_height = value.get().expect(&format!("Failed to set property `depth-height` on realsensesrc. Expected an int, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `depth-height` from {} to {}",
                    settings.streams.depth_resolution.height,
                    depth_height
                );
                settings.streams.depth_resolution.height = depth_height;
            }
            subclass::Property("color-width", ..) => {
                let color_width = value.get().expect(&format!("Failed to set property `color-width` on realsensesrc. Expected an int, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `color-width` from {} to {}",
                    settings.streams.color_resolution.width,
                    color_width
                );
                settings.streams.color_resolution.width = color_width;
            }
            subclass::Property("color-height", ..) => {
                let color_height = value.get().expect(&format!("Failed to set property `color-height` on realsensesrc. Expected an int, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `color-height` from {} to {}",
                    settings.streams.color_resolution.height,
                    color_height
                );
                settings.streams.color_resolution.height = color_height;
            }
            subclass::Property("framerate", ..) => {
                let framerate = value.get().expect(&format!("Failed to set property `framerate` on realsensesrc. Expected an int, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `framerate` from {} to {}",
                    settings.streams.framerate,
                    framerate
                );
                settings.streams.framerate = framerate;
                // let _ = element.post_message(&gst::Message::new_latency().src(Some(element)).build());
            }
            subclass::Property("loop-rosbag", ..) => {
                let loop_rosbag = value.get().expect(&format!("Failed to set property `loop-rosbag` on realsensesrc. Expected a boolean, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `loop-rosbag` from {} to {}",
                    settings.loop_rosbag,
                    loop_rosbag
                );
                settings.loop_rosbag = loop_rosbag;
            }
            subclass::Property("wait-for-frames-timeout", ..) => {
                let wait_for_frames_timeout = value.get().expect(&format!("Failed to set property `wait-for-frames-timeout` on realsensesrc. Expected an int, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `wait-for-frames-timeout` from {} to {}",
                    settings.wait_for_frames_timeout,
                    wait_for_frames_timeout
                );
                settings.wait_for_frames_timeout = wait_for_frames_timeout;
            }
            subclass::Property("include-per-frame-metadata", ..) => {
                let do_metadata = value.get().expect(&format!("Failed to set property `include-per-frame-metadata` on realsensesrc. Expected a boolean, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `include-per-frame-metadata` from {} to {}",
                    settings.include_per_frame_metadata,
                    do_metadata
                );
                settings.include_per_frame_metadata = do_metadata;
            }
            subclass::Property("timestamp-mode", ..) => {
                let timestamp_mode = value.get::<RealsenseTimestampMode>()
                    .expect(&format!("Failed to set property `timestamp-mode` on realsensesrc. Expected a i32 or RealsenseTimestampMode variant, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `do-custom-timestamp` from {:?} to {:?}",
                    settings.timestamp_mode,
                    timestamp_mode
                );
                settings.timestamp_mode = timestamp_mode;
            }
            subclass::Property("real-time-rosbag-playback", ..) => {
                let real_time_rosbag_playback = value.get().expect(&format!("Failed to set property `real-time-rosbag-playback` on realsensesrc. Expected a boolean, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `real-time-rosbag-playback` from {} to {}",
                    settings.real_time_rosbag_playback,
                    real_time_rosbag_playback
                );
                settings.real_time_rosbag_playback = real_time_rosbag_playback;
            }
            _ => unimplemented!("Property is not implemented"),
        };
    }

    fn get_property(&self, _obj: &glib::Object, id: usize) -> Result<glib::Value, ()> {
        let settings = &self
            .internals
            .lock()
            .expect("Could not lock internals")
            .settings;

        let prop = &PROPERTIES[id];
        match *prop {
            subclass::Property("serial", ..) => Ok(settings.serial.to_value()),
            subclass::Property("rosbag-location", ..) => Ok(settings.rosbag_location.to_value()),
            subclass::Property("json-location", ..) => Ok(settings.json_location.to_value()),
            subclass::Property("enable-depth", ..) => {
                Ok(settings.streams.enabled_streams.depth.to_value())
            }
            subclass::Property("enable-infra1", ..) => {
                Ok(settings.streams.enabled_streams.infra1.to_value())
            }
            subclass::Property("enable-infra2", ..) => {
                Ok(settings.streams.enabled_streams.infra2.to_value())
            }
            subclass::Property("enable-color", ..) => {
                Ok(settings.streams.enabled_streams.color.to_value())
            }
            subclass::Property("depth-width", ..) => {
                Ok(settings.streams.depth_resolution.width.to_value())
            }
            subclass::Property("depth-height", ..) => {
                Ok(settings.streams.depth_resolution.height.to_value())
            }
            subclass::Property("color-width", ..) => {
                Ok(settings.streams.color_resolution.width.to_value())
            }
            subclass::Property("color-height", ..) => {
                Ok(settings.streams.color_resolution.height.to_value())
            }
            subclass::Property("framerate", ..) => Ok(settings.streams.framerate.to_value()),
            subclass::Property("loop-rosbag", ..) => Ok(settings.loop_rosbag.to_value()),
            subclass::Property("wait-for-frames-timeout", ..) => {
                Ok(settings.wait_for_frames_timeout.to_value())
            }
            subclass::Property("include-per-frame-metadata", ..) => {
                Ok(settings.include_per_frame_metadata.to_value())
            }
            subclass::Property("timestamp-mode", ..) => Ok(settings.timestamp_mode.to_value()),
            subclass::Property("real-time-rosbag-playback", ..) => {
                Ok(settings.real_time_rosbag_playback.to_value())
            }
            _ => unimplemented!("Property is not implemented"),
        }
    }

    fn constructed(&self, obj: &glib::Object) {
        self.parent_constructed(obj);

        let element = obj
            .downcast_ref::<gst_base::BaseSrc>()
            .expect("Could not cast realsensesrc to BaseSrc");

        element.set_format(gst::Format::Time);
    }
}

impl ElementImpl for RealsenseSrc {}

impl BaseSrcImpl for RealsenseSrc {
    fn start(&self, element: &gst_base::BaseSrc) -> Result<(), gst::ErrorMessage> {
        // Lock the internals
        let internals = &mut self
            .internals
            .lock()
            .expect("Failed to obtain internals lock.");
        let settings = &internals.settings;

        // Make sure that the set properties are viable
        Self::check_internals(internals)?;

        // Specify realsense log severity level
        rs2::log::log_to_console(rs2::rs2_log_severity::RS2_LOG_SEVERITY_ERROR).map_err(|e| {
            gst_error_msg!(
                gst::ResourceError::OpenRead,
                [&format!("Cannot log librealsense to console: {}", e)]
            )
        })?;

        // Create new RealSense device config
        let config = rs2::config::Config::new().map_err(|e| {
            gst_error_msg!(
                gst::ResourceError::OpenRead,
                [&format!("Could not open RealSense device: {}", e)]
            )
        })?;

        // Based on properties, enable streaming, reading from or recording to a file (with the enabled streams)
        match &settings.serial {
            // A serial is specified. We attempt to open a live recording from the camera
            Some(serial) => {
                // Enable the selected streams
                Self::enable_streams(&config, &settings).map_err(|e| {
                    gst_error_msg!(
                        gst::ResourceError::OpenRead,
                        [&format!(
                            "Failed to enable a stream on `realsensesrc`: {:?}",
                            e
                        )]
                    )
                })?;

                // Enable device with the given serial number and device configuration
                config.enable_device(&serial).map_err(|_e| {
                    gst_error_msg!(
                        gst::ResourceError::Settings,
                        ["No device with serial `{}` is connected!", serial]
                    )
                })?;
            }

            // A serial was not specified, but a ROSBAG was, attempt to load that instead
            None => {
                let rosbag_location = settings.rosbag_location.as_ref().unwrap(); // we know this always works (see match condition)
                config
                    .enable_device_from_file_repeat_option(rosbag_location, settings.loop_rosbag)
                    .map_err(|e| {
                        gst_error_msg!(
                            gst::ResourceError::Settings,
                            ["Cannot read from \"{}\": {:?}!", rosbag_location, e]
                        )
                    })?;
            }
        }

        let pipeline = self
            .prepare_and_start_librealsense_pipeline(&config, &mut internals.settings)
            .map_err(|e| {
                gst_error_msg!(
                    gst::ResourceError::Settings,
                    ["Failed to prepare and start pipeline: {:?}", e]
                )
            })?;
        internals.state = State::Started { pipeline };

        gst_info!(self.cat, obj: element, "Streaming started");
        Ok(())
    }

    fn stop(&self, element: &gst_base::BaseSrc) -> Result<(), gst::ErrorMessage> {
        let state = &mut self
            .internals
            .lock()
            .expect("Could not lock internals")
            .state;

        match state {
            State::Started { ref pipeline } => {
                pipeline.stop().map_err(|e| {
                    gst_error_msg!(
                        gst::ResourceError::Settings,
                        ["RealSense pipeline could not be stopped: {:?}", e]
                    )
                })?;
                *state = State::Stopped;
            }
            State::Stopped => {
                unreachable!("Element is not yet started");
            }
        }

        self.parent_stop(element)
    }

    fn is_seekable(&self, _element: &gst_base::BaseSrc) -> bool {
        false
    }

    fn create(
        &self,
        element: &gst_base::BaseSrc,
        _offset: u64,
        _length: u32,
    ) -> Result<gst::Buffer, gst::FlowError> {
        let internals = &mut *self.internals.lock().expect("Failed to lock internals");
        let settings = &internals.settings;
        let streams = &settings.streams;

        // Get the RealSense pipeline
        let pipeline = match internals.state {
            State::Started { ref pipeline } => pipeline,
            State::Stopped => {
                unreachable!("Element is not yet started");
            }
        };

        let frames = pipeline
            .wait_for_frames(internals.settings.wait_for_frames_timeout)
            .map_err(|_| gst::FlowError::Eos)?;

        let timestamp = match settings.timestamp_mode {
            RealsenseTimestampMode::RS2 => {
                // Base timestamps on librealsense timestamps, div by 1000 to convert to seconds
                let rs2_timestamp = std::time::Duration::from_secs_f64(
                    frames[0]
                        .get_timestamp()
                        .map_err(|_| gst::FlowError::Error)?
                        / 1000.0,
                );
                // Initialise base_time based on first timestamp
                let base_time = &mut internals.base_time;
                if base_time.as_nanos() == 0 {
                    *base_time = rs2_timestamp;
                }
                // Compute difference between the current and the first timestamp
                let time_diff = rs2_timestamp
                    .checked_sub(*base_time)
                    .unwrap_or_else(|| unreachable!());
                Some(gst::ClockTime::from_nseconds(time_diff.as_nanos() as u64))
            }
            RealsenseTimestampMode::AllBuffers => {
                // Calculate a common `timestamp` if `do-custom-timestamp` is enabled, else set to None
                // This computation is similar to `gst_element_get_current_running_time` that will be
                // available in 1.18 https://gstreamer.freedesktop.org/documentation/gstreamer/
                // gstelement.html?gi-language=c#gst_element_get_current_running_time
                let element_clock = element.get_clock();
                if let Some(element_clock) = element_clock {
                    Some(element_clock.get_time() - element.get_base_time())
                } else {
                    None
                }
            }
            _ => None,
        };

        // Create the output buffer
        let mut output_buffer = gst::buffer::Buffer::new();

        let frame_duration = std::time::Duration::from_secs_f32(1.0_f32 / streams.framerate as f32);
        let gst_clock_frame_duration =
            gst::ClockTime::from_nseconds(frame_duration.as_nanos() as u64);

        // Attach `depth` frame if enabled
        if streams.enabled_streams.depth {
            self.extract_frame(
                &frames,
                &mut output_buffer,
                "depth",
                rs2::rs2_stream::RS2_STREAM_DEPTH,
                -1,
                &[],
                settings,
                timestamp,
                gst_clock_frame_duration,
            )?;
        }

        // Attach `infra1` frame if enabled
        if streams.enabled_streams.infra1 {
            self.extract_frame(
                &frames,
                &mut output_buffer,
                "infra1",
                rs2::rs2_stream::RS2_STREAM_INFRARED,
                1,
                &[streams.enabled_streams.depth],
                settings,
                timestamp,
                gst_clock_frame_duration,
            )?;
        }

        // Attach `infra2` frame if enabled
        if streams.enabled_streams.infra2 {
            self.extract_frame(
                &frames,
                &mut output_buffer,
                "infra2",
                rs2::rs2_stream::RS2_STREAM_INFRARED,
                2,
                &[
                    streams.enabled_streams.depth,
                    streams.enabled_streams.infra1,
                ],
                settings,
                timestamp,
                gst_clock_frame_duration,
            )?;
        }

        // Attach `color` frame if enabled
        if streams.enabled_streams.color {
            self.extract_frame(
                &frames,
                &mut output_buffer,
                "color",
                rs2::rs2_stream::RS2_STREAM_COLOR,
                -1,
                &[
                    streams.enabled_streams.depth,
                    streams.enabled_streams.infra1,
                    streams.enabled_streams.infra2,
                ],
                settings,
                timestamp,
                gst_clock_frame_duration,
            )?;
        }

        Ok(output_buffer)
    }

    fn fixate(&self, element: &gst_base::BaseSrc, caps: gst::Caps) -> gst::Caps {
        let settings = &self
            .internals
            .lock()
            .expect("Could not lock internals")
            .settings;

        let mut caps = gst::Caps::truncate(caps);
        {
            let caps = caps.make_mut();
            let s = caps
                .get_mut_structure(0)
                .expect("Failed to read the realsensesrc CAPS");

            // Create string containing selected streams with priority `depth` > `infra1` > `infra2` > `color`
            // The first stream in this string is contained in the main buffer
            let mut selected_streams = String::new();

            if settings.streams.enabled_streams.depth {
                // Add `depth` stream with its format, width and height into the caps if enabled
                selected_streams.push_str(&"depth,");
                s.set(
                    "depth_format",
                    &gst_video::VideoFormat::Gray16Le.to_string(),
                );
                s.set("depth_width", &settings.streams.depth_resolution.width);
                s.set("depth_height", &settings.streams.depth_resolution.height);
                if settings.include_per_frame_metadata {
                    selected_streams.push_str(&"depthmeta,");
                }
            }
            if settings.streams.enabled_streams.infra1 {
                // Add `infra1` stream with its format, width and height into the caps if enabled
                selected_streams.push_str(&"infra1,");
                s.set("infra1_format", &gst_video::VideoFormat::Gray8.to_string());
                s.set("infra1_width", &settings.streams.depth_resolution.width);
                s.set("infra1_height", &settings.streams.depth_resolution.height);
                if settings.include_per_frame_metadata {
                    selected_streams.push_str(&"infra1meta,");
                }
            }
            if settings.streams.enabled_streams.infra2 {
                // Add `infra2` stream with its format, width and height into the caps if enabled
                selected_streams.push_str(&"infra2,");
                s.set("infra2_format", &gst_video::VideoFormat::Gray8.to_string());
                s.set("infra2_width", &settings.streams.depth_resolution.width);
                s.set("infra2_height", &settings.streams.depth_resolution.height);
                if settings.include_per_frame_metadata {
                    selected_streams.push_str(&"infra2meta,");
                }
            }
            if settings.streams.enabled_streams.color {
                // Add `color` stream with its format, width and height into the caps if enabled
                selected_streams.push_str(&"color,");
                s.set("color_format", &gst_video::VideoFormat::Rgb.to_string());
                s.set("color_width", &settings.streams.color_resolution.width);
                s.set("color_height", &settings.streams.color_resolution.height);
                if settings.include_per_frame_metadata {
                    selected_streams.push_str(&"colormeta,");
                }
            }

            // Pop the last ',' contained in streams (not really necessary, but nice)
            selected_streams.pop();

            // Finally add the streams to the caps
            s.set("streams", &selected_streams.as_str());

            // Fixate the framerate
            s.fixate_field_nearest_fraction("framerate", settings.streams.framerate);
        }
        self.parent_fixate(element, caps)
    }
}

impl RealsenseSrc {
    /// Prepare a librealsense pipeline, which can read frames from a RealSense camera, using the
    /// given `config` and `settings`. If the preparation succeeds, the pipeline is started. The
    /// function returns a `RealsenseError` if any of those operations fails.
    /// # Arguments
    /// * `config` - The librealsense configuration to use for the camera.
    /// * `settings` - The settings for the realsensesrc.
    fn prepare_and_start_librealsense_pipeline(
        &self,
        config: &rs2::config::Config,
        settings: &mut Settings,
    ) -> Result<rs2::pipeline::Pipeline, RealsenseError> {
        // Get context and a list of connected devices
        let context = rs2::context::Context::new()?;

        // Load JSON if `json-location` is defined
        let devices = context.query_devices()?;

        if settings.json_location.is_some() && settings.serial.is_some() {
            Self::load_json(
                &devices,
                &settings.serial.clone().unwrap(),
                &settings.json_location.clone().unwrap(),
            )?;
        }

        // Start the RealSense pipeline
        let pipeline = rs2::pipeline::Pipeline::new(&context)?;
        let pipeline_profile = pipeline.start_with_config(&config)?;

        // If playing from a rosbag recording, check whether the correct properties were selected
        // and update them
        if settings.rosbag_location.is_some() {
            self.configure_rosbag_settings(&mut *settings, &pipeline_profile)?;
        }

        Ok(pipeline)
    }

    /// Check the settings for the realsensesrc to verify that the user of the plugin has specified
    /// a valid configuration.
    /// # Arguments
    /// * `internals` - The current settings for the `realsensesrc`.
    fn check_internals(internals: &RealsenseSrcInternals) -> Result<(), gst::ErrorMessage> {
        let settings = &internals.settings;

        // Make sure the pipeline has started
        if let State::Started { .. } = internals.state {
            unreachable!("Element has already started");
        }

        // Either `serial` or `rosbag-location` must be specified
        if settings.serial.is_none() && settings.rosbag_location.is_none() {
            return Err(gst_error_msg!(
                gst::ResourceError::Settings,
                ["Neither the `serial` or `rosbag-location` properties are defined. At least one of these must be defined!"]
            ));
        }

        // At least one stream must be enabled
        if !settings.streams.enabled_streams.any() {
            return Err(gst_error_msg!(
                gst::ResourceError::Settings,
                ["No stream is enabled. At least one stream must be enabled!"]
            ));
        }

        Ok(())
    }

    /// Enable all the streams that has their associated property set to `true`. This function
    /// returns an error if any streams cannot be enabled.
    /// # Arguments
    /// * `config` - The realsense configuration, which may be used to enable streams.
    /// * `settings` - The settings for the realsensesrc, which in this case specifies which streams to enable.
    fn enable_streams(
        config: &rs2::config::Config,
        settings: &Settings,
    ) -> Result<(), StreamEnableError> {
        if settings.streams.enabled_streams.depth {
            config
                .enable_stream(
                    rs2::rs2_stream::RS2_STREAM_DEPTH,
                    -1,
                    settings.streams.depth_resolution.width,
                    settings.streams.depth_resolution.height,
                    rs2::rs2_format::RS2_FORMAT_Z16,
                    settings.streams.framerate,
                )
                .map_err(|_e| StreamEnableError("Depth stream"))?;
        }
        if settings.streams.enabled_streams.infra1 {
            config
                .enable_stream(
                    rs2::rs2_stream::RS2_STREAM_INFRARED,
                    1,
                    settings.streams.depth_resolution.width,
                    settings.streams.depth_resolution.height,
                    rs2::rs2_format::RS2_FORMAT_Y8,
                    settings.streams.framerate,
                )
                .map_err(|_e| StreamEnableError("Infra1 stream"))?;
        }
        if settings.streams.enabled_streams.infra2 {
            config
                .enable_stream(
                    rs2::rs2_stream::RS2_STREAM_INFRARED,
                    2,
                    settings.streams.depth_resolution.width,
                    settings.streams.depth_resolution.height,
                    rs2::rs2_format::RS2_FORMAT_Y8,
                    settings.streams.framerate,
                )
                .map_err(|_e| StreamEnableError("Infra2 stream"))?;
        }
        if settings.streams.enabled_streams.color {
            config
                .enable_stream(
                    rs2::rs2_stream::RS2_STREAM_COLOR,
                    -1,
                    settings.streams.color_resolution.width,
                    settings.streams.color_resolution.height,
                    rs2::rs2_format::RS2_FORMAT_RGB8,
                    settings.streams.framerate,
                )
                .map_err(|_e| StreamEnableError("Color stream"))?;
        }
        Ok(())
    }

    /// Configure the device with the given `serial` with the JSON file specified on the given
    /// `json_location`.
    /// # Arguments
    /// * `devices` - A list of all available devices.
    /// * `serial` - The serial number of the device to configure.
    /// * `json_location` - The absolute path to the file containing the JSON configuration.
    fn load_json(
        devices: &Vec<rs2::device::Device>,
        serial: &str,
        json_location: &str,
    ) -> Result<(), RealsenseError> {
        // Make sure a device with the selected serial is connected
        // Find the device with the given serial, ignoring all errors
        let device = devices
            .iter()
            .find(
                |d| match d.get_info(rs2::rs2_camera_info::RS2_CAMERA_INFO_SERIAL_NUMBER) {
                    Ok(device_serial) => *serial == device_serial,
                    _ => false,
                },
            )
            .ok_or(RealsenseError(format!(
                "Could not find a device with id: {}",
                serial
            )))?;

        if !device.is_advanced_mode_enabled()? {
            device.set_advanced_mode(true)?;
        }
        let json_content = std::fs::read_to_string(json_location).map_err(|e| {
            RealsenseError(format!(
                "Cannot read RealSense configuration from \"{}\": {:?}",
                json_location.clone(),
                e
            ))
        })?;

        device.load_json(&json_content)?;
        Ok(())
    }

    /// Attempt to read the metadata from the given frame and serialize it using CapnProto. If this
    /// function returns `None`, it prints a warning to console that explains the issue.
    /// # Arguments
    /// * `frame` - The frame to read and serialize metadata for.
    /// * `element` - The element that represents the realsensesrc.
    fn get_frame_meta(&self, frame: &rs2::frame::Frame) -> Result<Vec<u8>, RealsenseError> {
        let frame_meta = frame.get_metadata().map_err(|e| {
            RealsenseError(format!(
                "Failed to read metadata from RealSense camera: {}",
                e
            ))
        })?;
        capnp_serialize(frame_meta).map_err(|e| {
            RealsenseError(format!(
                "Failed to serialize metadata from RealSense camera: {}",
                e
            ))
        })
    }

    /// Attempt to add `frame_meta` as a gst meta buffer onto `buffer`. This function simply ignores
    /// cases there `frame_meta` is `None`.
    /// # Arguments
    /// * `buffer` - The gst::Buffer to which the metadata should be added.
    /// * `frame_meta` - A byte vector containing the serialized metadata.
    /// * `tag` - The tag of the stream.
    /// * `timestamp` - The timestamp of the buffer.
    /// * `frame_duration` - The duration of the buffer.
    fn add_per_frame_metadata(
        &self,
        buffer: &mut gst::Buffer,
        frame_meta: Vec<u8>,
        tag: &str,
        timestamp: Option<gst::ClockTime>,
        duration: gst::ClockTime,
    ) {
        // If we were able to read some metadata add it to the buffer
        let mut frame_meta_buffer = gst::buffer::Buffer::from_slice(frame_meta);

        let tag_name = format!("{}meta", tag);
        let mut tags = gst::tags::TagList::new();
        tags.get_mut()
            .expect("Cannot get mutable reference to `tags`")
            .add::<gst::tags::Title>(&tag_name.as_str(), gst::TagMergeMode::Append);

        let frame_meta_mut = frame_meta_buffer
            .get_mut()
            .expect("Could not add tags to `frame_meta_buffer`");
        TagsMeta::add(frame_meta_mut, &mut tags);
        if let Some(ts) = timestamp {
            frame_meta_mut.set_dts(ts);
            frame_meta_mut.set_pts(ts);
        }
        frame_meta_mut.set_duration(duration);

        BufferMeta::add(
            buffer
                .get_mut()
                .expect("Could not add `frame_meta_buffer` onto frame buffer."),
            &mut frame_meta_buffer,
        );
    }

    /// Extract a frame from the RealSense camera, outputting it in `output_buffer` on the given
    /// `element`. This function outputs the frame as main buffer if `previous_streams` is empty or
    /// all `false` and as a meta buffer if `previous_streams` contains any `true`s.
    /// # Arguments
    /// * `element` - The element that represents the `realsensesrc`.
    /// * `frames` - A collection of frames that was extracted from the RealSense camera (or ROSBAG)
    /// * `output_buffer` - The buffer which the frames should be extracted into.
    /// * `tag` - The tag to give to the buffer. This may be used to identify the type of the stream later downstream.
    /// * `stream_type` - The type of the stream we should extract.
    /// * `stream_id` - The id of the stream to extract.
    /// * `previous_streams` - A list of booleans. If any is ticked, it means we should extract the next frame as secondary buffer.
    /// * `settings` - The settings for the `realsensesrc`.
    /// * `timestamp` - The timestamp to give to the frame.
    fn extract_frame(
        &self,
        frames: &Vec<rs2::frame::Frame>,
        output_buffer: &mut gst::Buffer,
        tag: &str,
        stream_type: rs2::rs2_stream,
        stream_id: i32,
        previous_streams: &[bool],
        settings: &Settings,
        timestamp: Option<gst::ClockTime>,
        frame_duration: gst::ClockTime,
    ) -> Result<(), RealsenseError> {
        // Extract the frame from frames based on its type and id
        let frame = find_frame_with_id(frames, stream_type, stream_id).ok_or(RealsenseError(
            "Failed to find a suitable frame on realsensesrc".to_owned(),
        ))?;

        // Create the appropriate tag
        let mut tags = gst::tags::TagList::new();
        tags.get_mut()
            .expect("Could not get mutable reference to `tags`")
            .add::<gst::tags::Title>(&tag, gst::TagMergeMode::Append);

        // Extract the frame data into a new buffer
        let frame_data = frame
            .get_data()
            .map_err(|e| RealsenseError(e.get_message()))?;
        let mut buffer = gst::buffer::Buffer::from_mut_slice(frame_data);

        let buffer_mut_ref = buffer
            .get_mut()
            .expect("Could not get a mutable reference to the buffer");

        // Add tag to this new buffer
        TagsMeta::add(buffer_mut_ref, &mut tags);

        // Set timestamp
        if let Some(timestamp) = timestamp {
            buffer_mut_ref.set_pts(timestamp);
            buffer_mut_ref.set_dts(timestamp);
        };
        buffer_mut_ref.set_duration(frame_duration);

        // Determine whether any of the previous streams is enabled
        let is_earlier_stream_enabled = previous_streams.iter().any(|s| *s);

        // Where the buffer is placed depends whether this is the first stream that is enabled
        if is_earlier_stream_enabled {
            // Attach this new buffer as meta to the output buffer
            BufferMeta::add(
                output_buffer
                    .get_mut()
                    .expect("Could not get mutable reference to `output_buffer`"),
                &mut buffer,
            );
        } else {
            // Else put this frame into the output buffer
            *output_buffer = buffer;
            // Add the tag
            TagsMeta::add(
                output_buffer
                    .get_mut()
                    .expect("Could not get mutable reference to `output_buffer`"),
                &mut tags,
            );
        }

        // Check if we should attach RealSense per-frame meta and do that if so
        if settings.include_per_frame_metadata {
            // Attempt to read the RealSense per-frame metadata, otherwise set frame_meta to None
            let md = self.get_frame_meta(frame)?;
            self.add_per_frame_metadata(output_buffer, md, tag, timestamp, frame_duration);
        }

        Ok(())
    }

    /// Check if the selected settings match enabled streams and their properties in rosbag file.
    /// If an enabled stream is not contained within a rosbag recording, this function returns
    /// error. If different stream resolutions or a different framerate were selected, this
    /// function updates them appropriately based on the information contained within the rosbag
    /// recording.
    ///
    /// # Arguments
    /// * `stream_settings` - The settings selected for the streams.
    /// * `pipeline_profile` - The profile of the current realsense pipeline.
    ///
    /// # Returns
    /// * `Ok()` if all enabled streams are available. Settings for these streams might get updated.
    /// * `Err(RealsenseError)` if an enabled stream is not available in rosbag recording.
    fn configure_rosbag_settings(
        &self,
        settings: &mut Settings,
        pipeline_profile: &rs2::pipeline_profile::PipelineProfile,
    ) -> Result<(), RealsenseError> {
        let stream_settings = &mut settings.streams;
        // Get information about the streams in the rosbag recording.
        let streams_info = rs2::high_level_utils::get_info_all_streams(pipeline_profile)?;

        // Create a struct of enabled streams that is later used to check whether some of the
        // enabled streams if not contained in the rosbag recording.
        let mut rosbag_enabled_streams = EnabledStreams {
            depth: false,
            infra1: false,
            infra2: false,
            color: false,
        };

        // Iterate over all streams contained in the rosbag recording
        for stream_info in streams_info.iter() {
            self.update_settings_from_rosbag(
                stream_info,
                stream_settings,
                &mut rosbag_enabled_streams,
            );
        }

        // Return error if at least of the enabled streams is not contained within the
        // rosbag recording.
        self.check_if_streams_are_available(
            &stream_settings.enabled_streams,
            &rosbag_enabled_streams,
        )?;

        // Set real-time playback based on property
        let playback =
            rs2::record_playback::Playback::create_from_pipeline_profile(pipeline_profile)?;
        playback.set_real_time(settings.real_time_rosbag_playback)?;

        Ok(())
    }

    /// Update stream resolutions or framerate if there is a conflict between settings and the
    /// rosbag recording.
    ///
    /// # Arguments
    /// * `stream_info` - The information of a stream obtained from rosbag recording.
    /// * `stream_settings` - The settings selected for the streams.
    /// * `rosbag_enabled_streams` - A list of what streams are enabled in the rosbag.
    fn update_settings_from_rosbag(
        &self,
        stream_info: &StreamInfo,
        stream_settings: &mut Streams,
        rosbag_enabled_streams: &mut EnabledStreams,
    ) {
        // Determine what stream to consider
        match stream_info.data.stream {
            // Consider `depth` stream
            rs2::rs2_stream::RS2_STREAM_DEPTH => {
                rosbag_enabled_streams.depth = true;

                // Uptade `depth` stream, if applicable
                self.update_stream(
                    "depth",
                    stream_info,
                    &stream_settings.enabled_streams.depth,
                    &mut stream_settings.depth_resolution,
                    &mut stream_settings.framerate,
                );
            }

            // Consider one of `infraX` streams
            rs2::rs2_stream::RS2_STREAM_INFRARED => {
                match stream_info.data.index {
                    // Consider `infra1`
                    1 => {
                        rosbag_enabled_streams.infra1 = true;

                        // Uptade `infra1` stream, if applicable
                        self.update_stream(
                            "infra1",
                            stream_info,
                            &stream_settings.enabled_streams.infra1,
                            &mut stream_settings.depth_resolution,
                            &mut stream_settings.framerate,
                        );
                    }
                    // Consider `infra2`
                    2 => {
                        rosbag_enabled_streams.infra2 = true;

                        // Uptade `infra2` stream, if applicable
                        self.update_stream(
                            "infra2",
                            stream_info,
                            &stream_settings.enabled_streams.infra2,
                            &mut stream_settings.depth_resolution,
                            &mut stream_settings.framerate,
                        );
                    }
                    // There are only 2 sensors in a binocular stereo setup
                    _ => unimplemented!(),
                }
            }

            // Consider `color`
            rs2::rs2_stream::RS2_STREAM_COLOR => {
                rosbag_enabled_streams.color = true;

                // Uptade `color` stream, if applicable
                self.update_stream(
                    "color",
                    stream_info,
                    &stream_settings.enabled_streams.color,
                    &mut stream_settings.color_resolution,
                    &mut stream_settings.framerate,
                );
            }
            // No other streams are expected
            _ => unimplemented!(),
        }
    }

    /// Update stream resolutions or framerate if there is a conflict between settings and the
    /// rosbag recording.
    ///
    /// # Arguments
    /// * `stream_id` - The identifier of the stream.
    /// * `stream_settings_enabled` - Determines whether the stream enabled.
    /// * `stream_settings_resolution` - The selected resolution of the stream.
    /// * `stream_settings_framerate` - The selected framerate of the stream.
    /// * `stream_info` - The informaton about the stream from rosbag recording.
    fn update_stream(
        &self,
        stream_id: &str,
        stream_info: &StreamInfo,
        stream_settings_enabled: &bool,
        stream_settings_resolution: &mut StreamResolution,
        stream_settings_framerate: &mut i32,
    ) {
        // There is no need to update if the stream is not even enabled.
        if *stream_settings_enabled {
            // Update the stream resolution, if applicable
            self.update_resolution_based_on_rosbag(
                stream_id,
                stream_settings_resolution,
                &stream_info.resolution,
            );

            // Update the stream framerate, if applicable
            self.update_framerate_based_on_rosbag(
                stream_id,
                stream_settings_framerate,
                &stream_info.data.framerate,
            );
        } else {
            // Notify STDOUT that there is a stream that was not enabled
            gst_info!(
                self.cat,
                "There is a `{}` stream contained within the rosbag recording that was not enabled.", stream_id
            );
        }
    }

    /// Update settings for the resolution of a stream if a conflict with rosbag is detected.
    ///
    /// # Arguments
    /// * `stream_id` - The identifier of the stream.
    /// * `settings_resolution` - The resolution selected in the settings stream.
    /// * `rosbag_resolution` - The actual resolution of the rosbag stream.
    fn update_resolution_based_on_rosbag(
        &self,
        stream_id: &str,
        settings_resolution: &mut StreamResolution,
        rosbag_resolution: &StreamResolution,
    ) {
        if settings_resolution != rosbag_resolution {
            gst_warning!(
                self.cat,
                "The selected resolution of {}x{} px for the `{}` stream differs from the resolution in the rosbag recording. Setting the stream's resolution to {}x{} px.",
                settings_resolution.width,
                settings_resolution.height,
                stream_id,
                rosbag_resolution.width,
                rosbag_resolution.height
            );
            *settings_resolution = rosbag_resolution.clone();
        }
    }

    /// Update settings for the framerate of a stream if a conflict with rosbag is detected.
    ///
    /// # Arguments
    /// * `stream_id` - The identifier of the stream.
    /// * `settings_framerate` - The framerate selected in the settings stream.
    /// * `rosbag_framerate` - The actual framerate of the rosbag stream.
    fn update_framerate_based_on_rosbag(
        &self,
        stream_id: &str,
        settings_framerate: &mut i32,
        rosbag_framerate: &i32,
    ) {
        if settings_framerate != rosbag_framerate {
            gst_warning!(
                self.cat,
                "The selected framerate of {} fps for the `{}` stream differs from the framerate in the rosbag recording. Setting the stream's framerate to {} fps.",
                settings_framerate,
                stream_id,
                rosbag_framerate,
            );
            *settings_framerate = rosbag_framerate.clone();
        }
    }

    /// Check if all the enabled streams are available.
    ///
    /// # Arguments
    /// * `enabled_streams` - The selected streams.
    /// * `available_streams` - The actual available streams.
    ///
    /// # Returns
    /// * `Ok()` if all enabled streams are available.
    /// * `Err(RealsenseError)` if an enabled stream is not available.
    fn check_if_streams_are_available(
        &self,
        enabled_streams: &EnabledStreams,
        available_streams: &EnabledStreams,
    ) -> Result<(), RealsenseError> {
        let conflicting_streams: Vec<&str> =
            EnabledStreams::get_conflicts(enabled_streams, available_streams);

        if !conflicting_streams.is_empty() {
            return Err(RealsenseError(format!(
                "The following stream(s) `{:?}` are not available in the rosbag recording.",
                conflicting_streams,
            )));
        }

        Ok(())
    }
}

/// Attempt to find the frame for the given `stream_id` in the Vector of frames extracted from the
/// RealSense camera. This function returns `None` on missing or erroneous frames.
/// # Arguments
/// * `frames` - A vector of frames extracted from librealsense.
/// * `stream_type` - The type of the stream to look for.
/// * `stream_id` - The id of the frame you wish to find.
fn find_frame_with_id(
    frames: &Vec<rs2::frame::Frame>,
    stream_type: rs2::rs2_stream,
    stream_id: i32,
) -> Option<&rs2::frame::Frame> {
    frames.iter().find(|f| match f.get_stream_profile() {
        Ok(profile) => match profile.get_data() {
            Ok(data) => {
                data.stream == stream_type
                    && if stream_id == -1 {
                        true
                    } else {
                        data.index == stream_id
                    }
            }
            _ => false,
        },
        _ => false,
    })
}

pub fn register(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    gst::Element::register(
        Some(plugin),
        "realsensesrc",
        gst::Rank::None,
        RealsenseSrc::get_type(),
    )
}
