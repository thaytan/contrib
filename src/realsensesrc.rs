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

use std::collections::HashMap;
use std::{
    convert::TryInto,
    sync::{Arc, Mutex},
};

use glib::subclass;
use gst::subclass::prelude::*;
use gst_base::prelude::*;
use gst_base::subclass::base_src::CreateSuccess;
use gst_base::subclass::prelude::*;

use camera_meta::Distortion;
use gst_depth_meta::{camera_meta, camera_meta::*, rgbd, rgbd_timestamps::*};
use rs2::high_level_utils::StreamInfo;

use crate::errors::*;
use crate::properties::*;
use crate::rs_meta::rs_meta_serialization::*;
use crate::settings::*;

lazy_static! {
    static ref CAT: gst::DebugCategory = gst::DebugCategory::new(
        "realsensesrc",
        gst::DebugColorFlags::empty(),
        Some("Realsense Source"),
    );
}

/// A struct representation of the `realsensesrc` element
struct RealsenseSrc {
    internals: Mutex<RealsenseSrcInternals>,
    /// Contains timestamp internals utilised by `RgbdTimestamps` trait.
    timestamp_internals: Arc<Mutex<TimestampInternals>>,
}

/// Internals of the element that are under Mutex
struct RealsenseSrcInternals {
    settings: Settings,
    state: State,
    /// Contains CameraMeta serialised with Cap'n Proto. Valid only if `attach-camera-meta=true`, otherwise empty.
    camera_meta_serialised: Vec<u8>,
}

/// An enum containing the current state of the RealSense pipeline
enum State {
    Stopped,
    Started { pipeline: rs2::pipeline::Pipeline },
}

impl RealsenseSrcInternals {
    /// Configure the realsense pipeline, checking the settings for the realsensesrc to verify that the user of the plugin has specified a valid configuration.
    /// # Returns
    /// - Ok(rs2::config::Config) if realsenesrc could be configured to use serial or rosbag
    /// - Err() if
    ///   - Neither serial, nor rosbag_location are specified
    ///   - BOTH serial and rosbag_location are specified
    ///   - No streams are enabled
    /// # Panics
    /// - Does not panic
    fn configure(&self) -> Result<rs2::config::Config, RealsenseError> {
        let settings = &self.settings;

        // Create new RealSense device config
        let config = rs2::config::Config::new()?;

        // Make sure the pipeline has started
        if let State::Started { .. } = self.state {
            unreachable!("Element has already started");
        }

        // Either `serial` or `rosbag-location` must be specified
        match (&settings.serial, &settings.rosbag_location) {
            (None, None) => {
                return Err(RealsenseError("Neither the `serial` or `rosbag-location` properties are defined. At least one of these must be defined!".to_string()));
            }
            // Make sure that only one stream source is selected
            (Some(serial), Some(rosbag_location)) => {
                return Err(RealsenseError(format!("Both `serial`: {:?} and `rosbag-location`: {:?} are defined. Only one of these can be defined!", serial, rosbag_location)))
            }
            // A serial is specified. We attempt to open a live recording from the camera
            (Some(serial), _) => {
                // Enable the selected streams
                Self::enable_streams(&config, &settings)?;

                // Enable device with the given serial number and device configuration
                config.enable_device(&serial)?;
            }
            // A serial was not specified, but a ROSBAG was, attempt to load that instead
            (None, Some(rosbag)) => {
                config.enable_device_from_file_repeat_option(&rosbag, settings.loop_rosbag)?;
            }
        }

        // At least one stream must be enabled
        if !settings.streams.enabled_streams.any() {
            return Err(RealsenseError(
                "No stream is enabled. At least one stream must be enabled!".to_string(),
            ));
        }

        Ok(config)
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

        // Install properties for streaming from RealSense
        klass.install_properties(PROPERTIES.as_ref());

        // Create src pad template with `video/rgbd` caps
        let src_caps = gst::Caps::new_simple(
            "video/rgbd",
            &[
                // List of available streams meant for indicating their respective priority
                (
                    "streams",
                    &"depth,infra1,infra2,color,depthmeta,infra1meta,infra2meta,colormeta,camerameta",
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
            internals: Mutex::new(RealsenseSrcInternals {
                settings: Settings::default(),
                state: State::Stopped,
                camera_meta_serialised: Vec::default(),
            }),
            timestamp_internals: Arc::new(Mutex::new(TimestampInternals::default())),
        }
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

        // Specify realsense log severity level
        rs2::log::log_to_console(rs2::rs2_log_severity::RS2_LOG_SEVERITY_ERROR).map_err(|e| {
            gst_error_msg!(
                gst::ResourceError::OpenRead,
                [&format!("Cannot log librealsense to console: {}", e)]
            )
        })?;

        // Make sure that the set properties are viable
        let config = internals.configure().map_err(|e| {
            let err_msg = format!("Failed to configure librealsense2 pipeline due to: {:?}", e);
            gst_error!(CAT, obj: element, "{}", &err_msg);
            gst_error_msg!(gst::ResourceError::Settings, (&err_msg))
        })?;

        let pipeline = self
            .prepare_and_start_librealsense_pipeline(element, &config, internals)
            .map_err(|e| {
                let err_msg = match e.0.as_str() {
                    "No device connected" => ConfigError::DeviceNotFound(
                        internals.settings.serial.as_ref().unwrap().clone(),
                    ),
                    "Couldn't resolve requests" => {
                        ConfigError::InvalidRequest(internals.settings.streams.clone())
                    }
                    _ => ConfigError::Other(e.0),
                };
                gst_error!(CAT, obj: element, "{}", &err_msg);
                gst_error_msg!(gst::ResourceError::Settings, ("{}", err_msg))
            })?;
        internals.state = State::Started { pipeline };

        gst_info!(CAT, obj: element, "Streaming started");
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
        _buffer: Option<&mut gst::BufferRef>,
        _length: u32,
    ) -> Result<CreateSuccess, gst::FlowError> {
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

        // Create the output buffer
        let mut output_buffer = gst::buffer::Buffer::new();

        // Attach `depth` frame if enabled
        if streams.enabled_streams.depth {
            self.attach_frame_to_buffer(
                element,
                settings,
                &mut output_buffer,
                &frames,
                "depth",
                -1,
                rs2::rs2_stream::RS2_STREAM_DEPTH,
                &[],
            )?;
        }

        // Attach `infra1` frame if enabled
        if streams.enabled_streams.infra1 {
            self.attach_frame_to_buffer(
                element,
                settings,
                &mut output_buffer,
                &frames,
                "infra1",
                1,
                rs2::rs2_stream::RS2_STREAM_INFRARED,
                &[streams.enabled_streams.depth],
            )?;
        }

        // Attach `infra2` frame if enabled
        if streams.enabled_streams.infra2 {
            self.attach_frame_to_buffer(
                element,
                settings,
                &mut output_buffer,
                &frames,
                "infra2",
                2,
                rs2::rs2_stream::RS2_STREAM_INFRARED,
                &[
                    streams.enabled_streams.depth,
                    streams.enabled_streams.infra1,
                ],
            )?;
        }

        // Attach `color` frame if enabled
        if streams.enabled_streams.color {
            self.attach_frame_to_buffer(
                element,
                settings,
                &mut output_buffer,
                &frames,
                "color",
                -1,
                rs2::rs2_stream::RS2_STREAM_COLOR,
                &[
                    streams.enabled_streams.depth,
                    streams.enabled_streams.infra1,
                    streams.enabled_streams.infra2,
                ],
            )?;
        }

        // Attach Cap'n Proto serialised `CameraMeta` if enabled
        if settings.attach_camera_meta {
            // An explicit clone of the serialised buffer is used so that CameraMeta does not need to be serialised every time.
            let camera_meta = internals.camera_meta_serialised.clone();
            self.attach_camera_meta(element, &mut output_buffer, camera_meta)?;
        }

        Ok(CreateSuccess::NewBuffer(output_buffer))
    }

    fn fixate(&self, element: &gst_base::BaseSrc, mut caps: gst::Caps) -> gst::Caps {
        let settings = &self
            .internals
            .lock()
            .expect("Could not lock internals")
            .settings;

        caps.truncate();
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

            // Add `camerameta` into `streams`, if enabled
            if settings.attach_camera_meta {
                selected_streams.push_str("camerameta,");
            }

            // Pop the last ',' contained in streams (not really necessary, but nice)
            selected_streams.pop();

            // Finally add the streams to the caps
            s.set("streams", &selected_streams.as_str());

            // Fixate the framerate
            s.fixate_field_nearest_fraction("framerate", settings.streams.framerate);
            // Send bus message to notify about a potential change in latency.
            let _ = element.post_message(gst::message::Latency::builder().src(element).build());
            // Update buffer duration for `RgbdTimestamps` trait
            self.set_buffer_duration(settings.streams.framerate as f32);
        }
        self.parent_fixate(element, caps)
    }

    // Handle queries such as the Latency query
    fn query(&self, element: &gst_base::BaseSrc, query: &mut gst::QueryRef) -> bool {
        use gst::QueryView;
        let settings = &self
            .internals
            .lock()
            .expect("Could not lock internals")
            .settings;

        match query.view_mut() {
            QueryView::Latency(ref mut q) => {
                let framerate: u64 = if let Ok(f) = settings.streams.framerate.try_into() {
                    f
                } else {
                    gst_error!(
                        CAT,
                        obj: element,
                        "Could not convert framerate: {} into u64",
                        settings.streams.framerate
                    );
                    return false;
                };

                // Setting latency to minimum of 1 frame - 1/framerate
                let latency = if let Some(l) = gst::SECOND.mul_div_floor(1, framerate) {
                    l
                } else {
                    // Return early if we are (most likely) dividing by zero.
                    gst_error!(
                        CAT,
                        obj: element,
                        "Could not compute latency, tried to divide 1/{}",
                        framerate
                    );
                    return false;
                };
                gst_debug!(CAT, obj: element, "Returning latency {}", latency);
                // Return latency
                q.set(element.is_live(), latency, gst::CLOCK_TIME_NONE);
                true
            }
            _ => BaseSrcImplExt::parent_query(self, element, query),
        }
    }
}

impl RealsenseSrc {
    /// Prepare a librealsense pipeline, which can read frames from a RealSense camera, using the
    /// given `config` and `settings`. If the preparation succeeds, the pipeline is started. The
    /// function returns a `RealsenseError` if any of those operations fails.
    /// # Arguments
    /// * `config` - The librealsense configuration to use for the camera.
    /// * `internals` - The internals of the realsensesrc.
    fn prepare_and_start_librealsense_pipeline(
        &self,
        element: &gst_base::BaseSrc,
        config: &rs2::config::Config,
        internals: &mut RealsenseSrcInternals,
    ) -> Result<rs2::pipeline::Pipeline, RealsenseError> {
        let settings = &mut internals.settings;

        // Get context and a list of connected devices
        let context = rs2::context::Context::new()?;
        let devices = context.query_devices()?;

        // Load JSON if `json-location` is defined
        if let (Some(json_location), Some(serial)) = (&settings.json_location, &settings.serial) {
            Self::load_json(&devices, &serial, &json_location)?;
        }

        // Crate new RealSense pipeline
        let pipeline = rs2::pipeline::Pipeline::new(&context)?;

        // Make sure that the config can be resolved
        config.resolve(&pipeline)?;

        // Start the RealSense pipeline
        let pipeline_profile = pipeline.start_with_config(&config)?;

        // If playing from a rosbag recording, check whether the correct properties were selected
        // and update them
        if settings.rosbag_location.is_some() {
            self.configure_rosbag_settings(&mut *settings, &pipeline_profile)?;
        }

        // Extract and print camera meta
        let camera_meta =
            Self::get_camera_meta(&settings.streams.enabled_streams, &pipeline_profile)?;
        gst_info!(
            CAT,
            obj: element,
            "RealSense stream source has the following calibration:\n{:?}",
            camera_meta
        );

        // Setup camera meta for transport, if enabled
        if settings.attach_camera_meta {
            // Serialise the CameraMeta
            internals.camera_meta_serialised = camera_meta
                .serialise()
                .map_err(|err| RealsenseError(format!("Cannot serialise camera meta: {}", err)))?;
        }

        Ok(pipeline)
    }

    /// Configure the device with the given `serial` with the JSON file specified on the given
    /// `json_location`.
    /// # Arguments
    /// * `devices` - A list of all available devices.
    /// * `serial` - The serial number of the device to configure.
    /// * `json_location` - The absolute path to the file containing the JSON configuration.
    fn load_json(
        devices: &[rs2::device::Device],
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
            .ok_or_else(|| {
                RealsenseError(format!("Could not find a device with id: {}", serial))
            })?;

        if !device.is_advanced_mode_enabled()? {
            device.set_advanced_mode(true)?;
        }
        let json_content = std::fs::read_to_string(json_location).map_err(|e| {
            RealsenseError(format!(
                "Cannot read RealSense configuration from \"{}\": {:?}",
                json_location, e
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
        let frame_meta = frame.get_metadata()?;
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
    fn add_per_frame_metadata(
        &self,
        element: &gst_base::BaseSrc,
        buffer: &mut gst::BufferRef,
        frame_meta: Vec<u8>,
        tag: &str,
    ) -> Result<(), RealsenseError> {
        // If we were able to read some metadata add it to the buffer
        let mut frame_meta_buffer = gst::buffer::Buffer::from_slice(frame_meta);

        // Set timestamps using `RgbdTimestamps` trait
        self.set_rgbd_timestamp(element, buffer, false, gst::CLOCK_TIME_NONE);

        // Attach the meta buffer and tag it adequately
        rgbd::attach_aux_buffer_and_tag(buffer, &mut frame_meta_buffer, &format!("{}meta", tag))?;

        Ok(())
    }

    /// Extract a frame from the RealSense camera, outputting it in `output_buffer` on the given
    /// `base_src`. This function outputs the frame as main buffer if `previous_streams` is empty or
    /// all `false` and as a meta buffer if `previous_streams` contains any `true`s.
    /// # Arguments
    /// * `base_src` - The element that represents the `realsensesrc`.
    /// * `settings` - The settings for the `realsensesrc`.
    /// * `output_buffer` - The buffer which the frames should be extracted into.
    /// * `frames` - A collection of frames that was extracted from the RealSense camera (or ROSBAG)
    /// * `tag` - The tag to give to the buffer. This may be used to identify the type of the stream later downstream.
    /// * `stream_id` - The id of the stream to extract.
    /// * `stream_type` - The type of the stream we should extract.
    /// * `previous_streams` - A list of booleans. If any is ticked, it means we should extract the next frame as secondary buffer.
    /// # TODO
    /// Refactor this function to have fewer arguments, as suggested by clippy.
    #[allow(clippy::too_many_arguments)]
    fn attach_frame_to_buffer(
        &self,
        base_src: &gst_base::BaseSrc,
        settings: &Settings,
        output_buffer: &mut gst::Buffer,
        frames: &[rs2::frame::Frame],
        tag: &str,
        stream_id: i32,
        stream_type: rs2::rs2_stream,
        previous_streams: &[bool],
    ) -> Result<(), RealsenseError> {
        // Extract the frame from frames based on its type and id
        let frame = Self::find_frame_with_id(frames, stream_type, stream_id).ok_or_else(|| {
            RealsenseError("Failed to find a suitable frame on realsensesrc".to_string())
        })?;

        // Extract the frame data into a new buffer
        let frame_data = frame
            .get_data()
            .map_err(|e| RealsenseError(e.get_message()))?;
        let mut buffer = gst::buffer::Buffer::from_mut_slice(frame_data);

        let buffer_mut_ref = buffer.get_mut().ok_or(gst_error_msg!(
            gst::ResourceError::Failed,
            [
                "Cannot get mutable reference to the buffer for {} stream",
                tag
            ]
        ))?;

        // Determine whether any of the previous streams is enabled
        let is_buffer_main = !previous_streams.iter().any(|stream| *stream);

        // Extract timestamp from RealSense frame, div by 1000 to convert to seconds
        let camera_timestamp = gst::ClockTime::from_nseconds(
            std::time::Duration::from_secs_f64(frame.get_timestamp()? / 1000.0).as_nanos() as u64,
        );

        // Set timestamps using `RgbdTimestamps` trait
        self.set_rgbd_timestamp(base_src, buffer_mut_ref, is_buffer_main, camera_timestamp);

        // Where the buffer is placed depends whether this is the first stream that is enabled
        if is_buffer_main {
            // Fill the main buffer and tag it adequately
            rgbd::fill_main_buffer_and_tag(output_buffer, buffer, tag)?;
        } else {
            // Attach the auxiliary buffer and tag it adequately
            rgbd::attach_aux_buffer_and_tag(
                output_buffer.get_mut().ok_or(gst_error_msg!(
                    gst::ResourceError::Failed,
                    [
                        "Cannot get mutable reference to the main buffer while attaching {} stream",
                        tag
                    ]
                ))?,
                &mut buffer,
                tag,
            )?;
        }

        // Check if we should attach RealSense per-frame meta and do that if so
        if settings.include_per_frame_metadata {
            // Attempt to read the RealSense per-frame metadata, otherwise set frame_meta to None
            let md = self.get_frame_meta(frame)?;
            self.add_per_frame_metadata(
                base_src,
                output_buffer.get_mut().ok_or(gst_error_msg!(
                    gst::ResourceError::Failed,
                    [
                        "Cannot get mutable reference to the main buffer while attaching {}meta",
                        tag
                    ]
                ))?,
                md,
                tag,
            )?;
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
                    stream_settings.enabled_streams.depth,
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
                            stream_settings.enabled_streams.infra1,
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
                            stream_settings.enabled_streams.infra2,
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
                    stream_settings.enabled_streams.color,
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
        stream_settings_enabled: bool,
        stream_settings_resolution: &mut StreamResolution,
        stream_settings_framerate: &mut i32,
    ) {
        // There is no need to update if the stream is not even enabled.
        if stream_settings_enabled {
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
                stream_info.data.framerate,
            );
        } else {
            // Notify STDOUT that there is a stream that was not enabled
            gst_info!(
                CAT,
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
                CAT,
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
        rosbag_framerate: i32,
    ) {
        if settings_framerate != &rosbag_framerate {
            gst_warning!(
                CAT,
                "The selected framerate of {} fps for the `{}` stream differs from the framerate in the rosbag recording. Setting the stream's framerate to {} fps.",
                settings_framerate,
                stream_id,
                rosbag_framerate,
            );
            *settings_framerate = rosbag_framerate;
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

    /// Sets up the serialised CameraMeta from Realsense PipelineProfile.
    ///
    /// # Arguments
    /// * `internals` - The internals of the element that contain settings and timestamp internals.
    /// * `pipeline_profile` - RealSense PipelineProfile.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(RealsenseError)` on failure.
    fn get_camera_meta(
        desired_streams: &EnabledStreams,
        pipeline_profile: &rs2::pipeline_profile::PipelineProfile,
    ) -> Result<CameraMeta, RealsenseError> {
        // Get the sensors and active stream profiles from the pipeline profile
        let sensors = pipeline_profile.get_device()?.query_sensors()?;
        let stream_profiles = pipeline_profile.get_streams()?;

        // Create intrinsics and insert the appropriate streams
        let intrinsics = Self::extract_intrinsics(desired_streams, &stream_profiles)?;

        // Create extrinsics and insert the appropriate transformations
        let extrinsics = Self::extract_extrinsics(desired_streams, &stream_profiles)?;

        // Create camera meta from the intrinsics, extrinsics and depth scale
        Ok(CameraMeta::new(
            intrinsics,
            extrinsics,
            Self::get_depth_scale(sensors),
        ))
    }

    /// Extract Intrinsics from the active RealSense stream profiles, while taking into account what streams are enabled.
    ///
    /// # Arguments
    /// * `desired_streams` - Desired streams.
    /// * `stream_profiles` - Active stream profiles.
    ///
    /// # Returns
    /// * `HashMap<String, camera_meta::Intrinsics>` containing Intrinsics corresponding to a stream.
    fn extract_intrinsics(
        desired_streams: &EnabledStreams,
        stream_profiles: &[rs2::stream_profile::StreamProfile],
    ) -> Result<HashMap<String, camera_meta::Intrinsics>, RealsenseError> {
        let mut intrinsics: HashMap<String, camera_meta::Intrinsics> = HashMap::new();

        // Iterate over all stream profile, extract intrinsics and assign them to the appropriate stream
        for stream_profile in stream_profiles.iter() {
            let stream_data = stream_profile.get_data()?;
            let stream_id = StreamId::from_rs2_stream(stream_data.stream, stream_data.index);

            // Make sure that the stream is enabled for streaming
            if Self::is_stream_enabled(stream_id, desired_streams) {
                intrinsics.insert(
                    stream_id.to_string(),
                    Self::rs2_intrinsics_to_camera_meta_intrinsics(
                        stream_profile.get_intrinsics()?,
                    ),
                );
            }
        }

        Ok(intrinsics)
    }

    /// Convert Realsense Extrinsics into CameraMeta Intrinsics.
    ///
    /// # Arguments
    /// * `rs2_intrinsics` - RealSense intrinsics to convert.
    ///
    /// # Returns
    /// * `camera_meta::Intrinsics` containing the converted intrinsics.
    fn rs2_intrinsics_to_camera_meta_intrinsics(
        rs2_intrinsics: rs2::intrinsics::Intrinsics,
    ) -> camera_meta::Intrinsics {
        use rs2::intrinsics::Distortion as rs2_dis;

        let distortion = match rs2_intrinsics.model {
            rs2_dis::RS2_DISTORTION_NONE => Distortion::None,
            rs2_dis::RS2_DISTORTION_MODIFIED_BROWN_CONRADY => Distortion::RsModifiedBrownConrady(
                camera_meta::RsCoefficients::from(rs2_intrinsics.coeffs),
            ),
            rs2_dis::RS2_DISTORTION_INVERSE_BROWN_CONRADY => Distortion::RsInverseBrownConrady(
                camera_meta::RsCoefficients::from(rs2_intrinsics.coeffs),
            ),
            rs2_dis::RS2_DISTORTION_FTHETA => {
                Distortion::RsFTheta(camera_meta::RsCoefficients::from(rs2_intrinsics.coeffs))
            }
            rs2_dis::RS2_DISTORTION_BROWN_CONRADY => {
                Distortion::RsBrownConrady(camera_meta::RsCoefficients::from(rs2_intrinsics.coeffs))
            }
            rs2_dis::RS2_DISTORTION_KANNALA_BRANDT4 => Distortion::RsKannalaBrandt4(
                camera_meta::RsCoefficients::from(rs2_intrinsics.coeffs),
            ),
            rs2_dis::RS2_DISTORTION_COUNT => {
                unreachable!("RS2_DISTORTION_COUNT is not a valid distotion model")
            }
        };

        camera_meta::Intrinsics {
            fx: rs2_intrinsics.fx,
            fy: rs2_intrinsics.fy,
            cx: rs2_intrinsics.ppx,
            cy: rs2_intrinsics.ppy,
            distortion,
        }
    }

    /// Extract extrinsics from the active RealSense stream profiles, while taking into account what streams are enabled.
    ///
    /// # Arguments
    /// * `desired_streams` - Desired streams.
    /// * `stream_profiles` - Active stream profiles.
    ///
    /// # Returns
    /// * `HashMap<(String, String), camera_meta::Transformation>` containing Transformation
    /// in a hashmap of <(from, to), Transformation>.
    fn extract_extrinsics(
        desired_streams: &EnabledStreams,
        stream_profiles: &[rs2::stream_profile::StreamProfile],
    ) -> Result<HashMap<(String, String), camera_meta::Transformation>, RealsenseError> {
        // Determine the main stream from which all transformations are taken
        let main_stream_id = Self::determine_main_stream(desired_streams);
        let (main_stream_rs2_stream, main_stream_rs2_index) = main_stream_id.to_rs2_stream();

        // Get the stream profile for the main stream
        let main_stream_profile = stream_profiles
            .iter()
            .find(|stream_profile| match stream_profile.get_data() {
                Ok(stream) => {
                    stream.stream == main_stream_rs2_stream
                        && if main_stream_rs2_index == -1 {
                            true
                        } else {
                            stream.index == main_stream_rs2_index
                        }
                }
                _ => false,
            })
            .expect("There is no stream profile for the primary enabled stream");

        // Iterate over all stream profiles and find extrinsics to the other enabled streams
        let mut extrinsics: HashMap<(String, String), camera_meta::Transformation> = HashMap::new();
        for stream_profile in stream_profiles.iter() {
            let stream_data = stream_profile.get_data()?;
            let stream_id = StreamId::from_rs2_stream(stream_data.stream, stream_data.index);

            if stream_id == main_stream_id {
                // Skip the main buffer
                continue;
            }

            // Make sure that the stream is enabled for streaming
            if Self::is_stream_enabled(stream_id, desired_streams) {
                extrinsics.insert(
                    (main_stream_id.to_string(), stream_id.to_string()),
                    Self::rs2_extrinsics_to_camera_meta_transformation(
                        main_stream_profile.get_extrinsics_to(stream_profile)?,
                    ),
                );
            }
        }

        Ok(extrinsics)
    }

    /// Convert RealSense Extrinsics into CameraMeta Transformation, which is used for creation of camera_meta::Extrinsics.
    ///
    /// # Arguments
    /// * `rs2_extrinsics` - Realsense extrinsics to convert.
    ///
    /// # Returns
    /// * `camera_meta::Transformation` containing the converted transformation.
    fn rs2_extrinsics_to_camera_meta_transformation(
        rs2_extrinsics: rs2::extrinsics::Extrinsics,
    ) -> camera_meta::Transformation {
        camera_meta::Transformation::new(
            camera_meta::Translation::from(rs2_extrinsics.translation),
            camera_meta::RotationMatrix::from(rs2_extrinsics.rotation),
        )
    }

    /// Extract the depth scale from RealSense Sensors.
    ///
    /// # Arguments
    /// * `sensors` - List of active RealSense sensors.
    ///
    /// # Returns
    /// * `f32` containing the depth scale, in metres. Default value of 0.001 is returned if depth sensor is not active.
    fn get_depth_scale(sensors: Vec<rs2::sensor::Sensor>) -> f32 {
        for sensor in sensors.iter() {
            let depth_scale = sensor.get_depth_scale();
            if let Ok(depth_scale) = depth_scale {
                // Return the depth scale as soon as it is found in sensors.
                return depth_scale;
            }
        }
        // If depth scale cannot be found (depth stream is not active), return the default depth scale.
        0.001
    }

    /// Attach Cap'n Proto serialised CameraMeta to `output_buffer`.
    ///
    /// # Arguments
    /// * `timestamp` - The timestamp of the buffer.
    /// * `frame_duration` - The duration of the buffer.
    /// * `output_buffer` - The output buffer to which the ImuSamples will be attached.
    /// * `camera_meta` - Serialised CameraMeta to attach to the `output_buffer`.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(RealsenseError)` on failure.
    fn attach_camera_meta(
        &self,
        element: &gst_base::BaseSrc,
        output_buffer: &mut gst::Buffer,
        camera_meta: Vec<u8>,
    ) -> Result<(), RealsenseError> {
        let camera_meta_stream_id = "camerameta";

        // Form a gst buffer out of mutable slice
        let mut buffer = gst::buffer::Buffer::from_mut_slice(camera_meta);
        // Get mutable reference to the buffer
        let buffer_mut_ref = buffer.get_mut().ok_or(gst_error_msg!(
            gst::ResourceError::Failed,
            [
                "Cannot get mutable reference to the buffer for {}",
                camera_meta_stream_id
            ]
        ))?;

        // Set timestamps using `RgbdTimestamps` trait
        self.set_rgbd_timestamp(element, buffer_mut_ref, false, gst::CLOCK_TIME_NONE);

        // Attach the camera_meta buffer and tag it adequately
        rgbd::attach_aux_buffer_and_tag(
            output_buffer.get_mut().ok_or(gst_error_msg!(
                gst::ResourceError::Failed,
                [
                    "Cannot get mutable reference to the main buffer while attaching {}",
                    camera_meta_stream_id
                ]
            ))?,
            &mut buffer,
            camera_meta_stream_id,
        )?;

        Ok(())
    }

    /// Determine the main stream, while taking into account the priority `depth > infra1 > infra2 > color`, and return the corresponding ID.
    ///
    /// # Arguments
    /// * `streams` - Struct containing enabled streams.
    ///
    /// # Returns
    /// * `&str` containing the ID of the main stream.
    fn determine_main_stream(streams: &EnabledStreams) -> StreamId {
        if streams.depth {
            StreamId::Depth
        } else if streams.infra1 {
            StreamId::Infra1
        } else if streams.infra2 {
            StreamId::Infra2
        } else {
            StreamId::Color
        }
    }

    /// Determines whether a specific stream id is enabled in `streams`.
    ///
    /// # Arguments
    /// * `stream_id` - Stream ID.
    /// * `streams` - Struct containing the enabled streams.
    ///
    /// # Returns
    /// * `true` if a stream with the `stream_id` is enabled, `false` otherwise .
    fn is_stream_enabled(stream_id: StreamId, streams: &EnabledStreams) -> bool {
        (stream_id == StreamId::Depth && streams.depth)
            || (stream_id == StreamId::Infra1 && streams.infra1)
            || (stream_id == StreamId::Infra2 && streams.infra2)
            || (stream_id == StreamId::Color && streams.color)
    }

    /// Attempt to find the frame for the given `stream_id` in the Vector of frames extracted from the
    /// RealSense camera. This function returns `None` on missing or erroneous frames.
    /// # Arguments
    /// * `frames` - A vector of frames extracted from librealsense.
    /// * `stream_type` - The type of the stream to look for.
    /// * `stream_id` - The id of the frame you wish to find.
    fn find_frame_with_id(
        frames: &[rs2::frame::Frame],
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
}

impl RgbdTimestamps for RealsenseSrc {
    fn get_timestamp_internals(&self) -> Arc<Mutex<TimestampInternals>> {
        self.timestamp_internals.clone()
    }
}

impl ObjectImpl for RealsenseSrc {
    glib_object_impl!();

    fn constructed(&self, obj: &glib::Object) {
        self.parent_constructed(obj);

        let element = obj
            .downcast_ref::<gst_base::BaseSrc>()
            .expect("Could not cast realsensesrc to BaseSrc");

        element.set_format(gst::Format::Time);
    }

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
                match value.get().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `serial` due to incorrect type: {:?}",
                        err
                    )
                }) {
                    Some(serial) => {
                        gst_info!(
                            CAT,
                            obj: element,
                            "Changing property `serial` from {:?} to {:?}",
                            settings.serial,
                            serial
                        );
                        settings.serial = Some(serial);
                        obj.downcast_ref::<gst_base::BaseSrc>()
                            .unwrap()
                            .set_live(true);
                    }
                    None => {
                        gst_warning!(
                            CAT,
                            obj: element,
                            "`serial` property not set, setting from {:?} to None",
                            settings.serial
                        );
                    }
                }
            }
            subclass::Property("rosbag-location", ..) => {
                match value.get().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `rosbag-location` due to incorrect type: {:?}",
                        err
                    )
                }) {
                    Some(mut rl) => {
                        expand_tilde_as_home_dir(&mut rl);
                        gst_info!(
                            CAT,
                            obj: element,
                            "Changing property `rosbag-location` from {:?} to {:?}",
                            settings.rosbag_location,
                            rl
                        );
                        settings.rosbag_location = Some(rl);
                        obj.downcast_ref::<gst_base::BaseSrc>()
                            .unwrap()
                            .set_live(settings.real_time_rosbag_playback);
                    }
                    None => {
                        gst_warning!(
                            CAT,
                            obj: element,
                            "`rosbag-location` property not set, setting from {:?} to None",
                            settings.rosbag_location
                        );
                    }
                }
            }
            subclass::Property("json-location", ..) => {
                match value.get().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `json-location` due to incorrect type: {:?}",
                        err
                    )
                }) {
                    Some(mut jl) => {
                        expand_tilde_as_home_dir(&mut jl);
                        gst_info!(
                            CAT,
                            obj: element,
                            "Changing property `json-location` from {:?} to {:?}",
                            settings.json_location,
                            jl
                        );
                        settings.json_location = Some(jl);
                    }
                    None => {
                        gst_info!(
                            CAT,
                            obj: element,
                            "`json-location` property not set, setting from {:?} to None",
                            settings.json_location,
                        );
                    }
                }
            }
            subclass::Property("enable-depth", ..) => {
                let enable_depth = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `enable-depth` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `enable-depth` from {} to {}",
                    settings.streams.enabled_streams.depth,
                    enable_depth
                );
                settings.streams.enabled_streams.depth = enable_depth;
            }
            subclass::Property("enable-infra1", ..) => {
                let enable_infra1 = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `enable-infra1` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `enable-infra1` from {} to {}",
                    settings.streams.enabled_streams.infra1,
                    enable_infra1
                );
                settings.streams.enabled_streams.infra1 = enable_infra1;
            }
            subclass::Property("enable-infra2", ..) => {
                let enable_infra2 = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `enable-infra2` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `enable-infra2` from {} to {}",
                    settings.streams.enabled_streams.infra2,
                    enable_infra2
                );
                settings.streams.enabled_streams.infra2 = enable_infra2;
            }
            subclass::Property("enable-color", ..) => {
                let enable_color = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `enable-color` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `enable-color` from {} to {}",
                    settings.streams.enabled_streams.color,
                    enable_color
                );
                settings.streams.enabled_streams.color = enable_color;
            }
            subclass::Property("depth-width", ..) => {
                let depth_width = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `depth-width` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `depth-width` from {} to {}",
                    settings.streams.depth_resolution.width,
                    depth_width
                );
                settings.streams.depth_resolution.width = depth_width;
            }
            subclass::Property("depth-height", ..) => {
                let depth_height = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `depth-height` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `depth-height` from {} to {}",
                    settings.streams.depth_resolution.height,
                    depth_height
                );
                settings.streams.depth_resolution.height = depth_height;
            }
            subclass::Property("color-width", ..) => {
                let color_width = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `color-width` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `color-width` from {} to {}",
                    settings.streams.color_resolution.width,
                    color_width
                );
                settings.streams.color_resolution.width = color_width;
            }
            subclass::Property("color-height", ..) => {
                let color_height = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `color-height` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `color-height` from {} to {}",
                    settings.streams.color_resolution.height,
                    color_height
                );
                settings.streams.color_resolution.height = color_height;
            }
            subclass::Property("framerate", ..) => {
                let framerate = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `framerate` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `framerate` from {} to {}",
                    settings.streams.framerate,
                    framerate
                );
                settings.streams.framerate = framerate;
                // let _ = element.post_message(&gst::Message::new_latency().src(Some(element)).build());
            }
            subclass::Property("loop-rosbag", ..) => {
                let loop_rosbag = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `loop-rosbag` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `loop-rosbag` from {} to {}",
                    settings.loop_rosbag,
                    loop_rosbag
                );
                settings.loop_rosbag = loop_rosbag;
            }
            subclass::Property("wait-for-frames-timeout", ..) => {
                let wait_for_frames_timeout = value.get_some().unwrap_or_else(|err| {panic!("Failed to set property `wait-for-frames-timeout` due to incorrect type: {:?}",err)});
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `wait-for-frames-timeout` from {} to {}",
                    settings.wait_for_frames_timeout,
                    wait_for_frames_timeout
                );
                settings.wait_for_frames_timeout = wait_for_frames_timeout;
            }
            subclass::Property("include-per-frame-metadata", ..) => {
                let do_metadata = value.get_some().unwrap_or_else(|err| {panic!("Failed to set property `include-per-frame-metadata` due to incorrect type: {:?}",err)});
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `include-per-frame-metadata` from {} to {}",
                    settings.include_per_frame_metadata,
                    do_metadata
                );
                settings.include_per_frame_metadata = do_metadata;
            }
            subclass::Property("real-time-rosbag-playback", ..) => {
                let real_time_rosbag_playback = value.get_some().unwrap_or_else(|err| {panic!("Failed to set property `real-time-rosbag-playback` due to incorrect type: {:?}",err)});
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `real-time-rosbag-playback` from {} to {}",
                    settings.real_time_rosbag_playback,
                    real_time_rosbag_playback
                );
                settings.real_time_rosbag_playback = real_time_rosbag_playback;
                obj.downcast_ref::<gst_base::BaseSrc>()
                    .unwrap()
                    .set_live(settings.real_time_rosbag_playback);
            }
            subclass::Property("attach-camera-meta", ..) => {
                let attach_camera_meta = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `attach-camera-meta` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `attach-camera-meta` from {} to {}",
                    settings.attach_camera_meta,
                    attach_camera_meta
                );
                settings.attach_camera_meta = attach_camera_meta;
            }
            subclass::Property("timestamp-mode", ..) => {
                let timestamp_mode = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "Failed to set property `timestamp-mode` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `timestamp-mode`  to {:?}",
                    timestamp_mode
                );
                self.set_timestamp_mode(element, timestamp_mode);
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
            subclass::Property("real-time-rosbag-playback", ..) => {
                Ok(settings.real_time_rosbag_playback.to_value())
            }
            subclass::Property("attach-camera-meta", ..) => {
                Ok(settings.attach_camera_meta.to_value())
            }
            subclass::Property("timestamp-mode", ..) => Ok(self
                .get_timestamp_internals()
                .lock()
                .unwrap()
                .timestamp_mode
                .to_value()),
            _ => unimplemented!("Property is not implemented"),
        }
    }
}

/// Helper function that replaces "~/" at the beginning of `path` with "$HOME/",
/// while `path` remains unchanged if it does not start with "~/".
fn expand_tilde_as_home_dir(path: &mut String) {
    if path.starts_with("~/") {
        let home_path = std::env::var("HOME")
        .expect("k4asrc: $HOME must be specified if a path for property is specified with \"~\" (tilde).");
        path.replace_range(..1, &home_path);
    }
}

pub fn register(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    gst::Element::register(
        Some(plugin),
        "realsensesrc",
        gst::Rank::None,
        RealsenseSrc::get_type(),
    )
}
