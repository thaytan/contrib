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

use crate::properties_d435;
use crate::properties_d435::DEFAULT_ENABLE_METADATA;
use crate::rs_meta::rs_meta_serialization::*;
use glib::subclass;
use gst::subclass::prelude::*;
use gst_base::prelude::*;
use gst_base::subclass::prelude::*;
use gst_depth_meta::buffer::BufferMeta;
use gst_depth_meta::tags::TagsMeta;
use rs2;
use std::error::Error;
use std::fmt;
use std::fmt::{Display, Formatter};
use std::sync::Mutex;

#[derive(Clone, Debug)]
struct StreamEnableError(&'static str);

impl Error for StreamEnableError {}

impl Display for StreamEnableError {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "Could not enable stream: {}", self.0)
    }
}

#[derive(Clone, Debug)]
struct RealsenseError(String);

impl Error for RealsenseError {}

impl Display for RealsenseError {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "Could not enable stream: {}", self.0)
    }
}

impl From<rs2::error::Error> for RealsenseError {
    fn from(error: rs2::error::Error) -> Self {
        Self(error.get_message())
    }
}

impl From<RealsenseError> for gst::FlowError {
    fn from(e: RealsenseError) -> Self {
        gst_error!(
            gst::DebugCategory::new(
                "realsensesrc",
                gst::DebugColorFlags::empty(),
                Some("Realsense Source"),
            ),
            "{}",
            e
        );
        gst::FlowError::Error
    }
}

// Default timeout used while waiting for frames from a realsense device in milliseconds.
const DEFAULT_PIPELINE_WAIT_FOR_FRAMES_TIMEOUT: u32 = 2500;
// Default behaviour of playing from rosbag recording specified by `rosbag-location` property.
const DEFAULT_LOOP_ROSBAG: bool = true;
// Default behaviour for adding custom timestamps to the buffers.
const DEFAULT_DO_CUSTOM_TIMESTAMP: bool = true;

static PROPERTIES: [subclass::Property; 16] = [
    subclass::Property("serial", |name| {
        glib::ParamSpec::string(
            name,
            "Serial Number",
            "Serial number of a realsense device. If unchanged or empty, `rosbag-location` is used to locate a file to play from.",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("rosbag-location", |name| {
        glib::ParamSpec::string(
            name,
            "Rosbag File Location",
            "Location of a rosbag file to play from. If unchanged or empty, physical device specified by `serial` is used.",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("json-location", |name| {
        glib::ParamSpec::string(
            name,
            "JSON File Location",
            "Location of a JSON file to load the RealSense device configuration from. This property applies only if `serial` is specified. If unchanged or empty, previous JSON configuration is used. If no previous configuration is present due to hardware reset, default configuration is used.",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable-depth", |name| {
        glib::ParamSpec::boolean(
            name,
            "Enable Depth",
            "Enables depth stream.",
            properties_d435::DEFAULT_ENABLE_DEPTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable-infra1", |name| {
        glib::ParamSpec::boolean(
            name,
            "Enable Infra1",
            "Enables infra1 stream.",
            properties_d435::DEFAULT_ENABLE_INFRA1,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable-infra2", |name| {
        glib::ParamSpec::boolean(
            name,
            "Enable Infra2",
            "Enables infra2 stream.",
            properties_d435::DEFAULT_ENABLE_INFRA2,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable-color", |name| {
        glib::ParamSpec::boolean(
            name,
            "Enable Color",
            "Enables color stream.",
            properties_d435::DEFAULT_ENABLE_COLOR,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("depth-width", |name| {
        glib::ParamSpec::int(
            name,
            "Depth Width",
            "Width of the depth and infra1/infra2 frames.",
            properties_d435::DEPTH_MIN_WIDTH,
            properties_d435::DEPTH_MAX_WIDTH,
            properties_d435::DEFAULT_DEPTH_WIDTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("depth-height", |name| {
        glib::ParamSpec::int(
            name,
            "Depth Height",
            "Height of the depth and infra1/infra2 frames.",
            properties_d435::DEPTH_MIN_HEIGHT,
            properties_d435::DEPTH_MAX_HEIGHT,
            properties_d435::DEFAULT_DEPTH_HEIGHT,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color-width", |name| {
        glib::ParamSpec::int(
            name,
            "Color Width",
            "Width of the color frame.",
            properties_d435::COLOR_MIN_WIDTH,
            properties_d435::COLOR_MAX_WIDTH,
            properties_d435::DEFAULT_COLOR_WIDTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color-height", |name| {
        glib::ParamSpec::int(
            name,
            "Color Height",
            "Height of the color frame.",
            properties_d435::COLOR_MIN_HEIGHT,
            properties_d435::COLOR_MAX_HEIGHT,
            properties_d435::DEFAULT_COLOR_HEIGHT,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("framerate", |name| {
        glib::ParamSpec::int(
            name,
            "Framerate",
            "Common framerate of the selected streams.",
            properties_d435::MIN_FRAMERATE,
            properties_d435::MAX_FRAMERATE,
            properties_d435::DEFAULT_FRAMERATE,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("loop-rosbag", |name| {
        glib::ParamSpec::boolean(
            name,
            "Loop Rosbag",
            "Enables looping of playing from rosbag recording specified by `rosbag-location` property. This property applies only if `rosbag-location` and no `serial` are specified.",
            DEFAULT_LOOP_ROSBAG,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("wait-for-frames-timeout", |name| {
        glib::ParamSpec::uint(
            name,
            "Wait For Frames Timeout",
            "Timeout used while waiting for frames from a RealSense device in milliseconds.",
            std::u32::MIN,
            std::u32::MAX,
            DEFAULT_PIPELINE_WAIT_FOR_FRAMES_TIMEOUT,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("include-per-frame-metadata", |name| {
        glib::ParamSpec::boolean(
            name,
            "Include Per Frame Metadata",
            "Adds librealsense2's per-frame metadata as an additional buffer on the video stream.",
            properties_d435::DEFAULT_ENABLE_METADATA,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("do-custom-timestamp", |name| {
        glib::ParamSpec::boolean(
            name,
            "Perform custom timestamp handling",
            "Adds timestamps to all buffers based on the duration since the element was created. As oppose to `do-timestamp`, this property adds the timestamps to all meta Buffers.",
            DEFAULT_DO_CUSTOM_TIMESTAMP,
            glib::ParamFlags::READWRITE,
        )
    }),
];

// A struct containing properties
struct Settings {
    serial: Option<String>,
    rosbag_location: Option<String>,
    json_location: Option<String>,
    streams: Streams,
    loop_rosbag: bool,
    wait_for_frames_timeout: u32,
    include_per_frame_metadata: bool,
    do_custom_timestamp: bool,
}

struct Streams {
    enable_depth: bool,
    enable_infra1: bool,
    enable_infra2: bool,
    enable_color: bool,
    depth_resolution: StreamResolution,
    color_resolution: StreamResolution,
    framerate: i32,
}

struct StreamResolution {
    width: i32,
    height: i32,
}

impl Default for Settings {
    fn default() -> Self {
        Settings {
            rosbag_location: None,
            serial: None,
            json_location: None,
            streams: Streams {
                enable_depth: properties_d435::DEFAULT_ENABLE_DEPTH,
                enable_infra1: properties_d435::DEFAULT_ENABLE_INFRA1,
                enable_infra2: properties_d435::DEFAULT_ENABLE_INFRA2,
                enable_color: properties_d435::DEFAULT_ENABLE_COLOR,
                depth_resolution: StreamResolution {
                    width: properties_d435::DEFAULT_DEPTH_WIDTH,
                    height: properties_d435::DEFAULT_DEPTH_HEIGHT,
                },
                color_resolution: StreamResolution {
                    width: properties_d435::DEFAULT_COLOR_WIDTH,
                    height: properties_d435::DEFAULT_COLOR_HEIGHT,
                },
                framerate: properties_d435::DEFAULT_FRAMERATE,
            },
            loop_rosbag: DEFAULT_LOOP_ROSBAG,
            wait_for_frames_timeout: DEFAULT_PIPELINE_WAIT_FOR_FRAMES_TIMEOUT,
            include_per_frame_metadata: DEFAULT_ENABLE_METADATA,
            do_custom_timestamp: DEFAULT_DO_CUSTOM_TIMESTAMP,
        }
    }
}

// An enum containing the current state of the RealSense pipeline
enum State {
    Stopped,
    Started { pipeline: rs2::pipeline::Pipeline },
}

impl Default for State {
    fn default() -> State {
        State::Stopped
    }
}

// A struct representation of the `realsensesrc` element
struct RealsenseSrc {
    cat: gst::DebugCategory,
    internals: Mutex<RealsenseSrcInternals>,
}

// Internals of the element that are under Mutex
struct RealsenseSrcInternals {
    settings: Settings,
    state: State,
    system_time: std::time::SystemTime,
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
                ("streams", &"depth,infra1,infra2,color"),
                (
                    "framerate",
                    &gst::FractionRange::new(
                        gst::Fraction::new(properties_d435::MIN_FRAMERATE, 1),
                        gst::Fraction::new(properties_d435::MAX_FRAMERATE, 1),
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
                state: State::default(),
                system_time: std::time::SystemTime::now(),
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
                    settings.streams.enable_depth,
                    enable_depth
                );
                settings.streams.enable_depth = enable_depth;
            }
            subclass::Property("enable-infra1", ..) => {
                let enable_infra1 = value.get().expect(&format!("Failed to set property `enable-infra` on realsensesrc. Expected a boolean, but got: {:?}", value));
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `enable-infra1` from {} to {}",
                    settings.streams.enable_infra1,
                    enable_infra1
                );
                settings.streams.enable_infra1 = enable_infra1;
            }
            subclass::Property("enable-infra2", ..) => {
                let enable_infra2 = value.get().expect(&format!("Failed to set property `enable-infra2` on realsensesrc. Expected a boolean, but got: {:?}", value));
                ;
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `enable-infra2` from {} to {}",
                    settings.streams.enable_infra2,
                    enable_infra2
                );
                settings.streams.enable_infra2 = enable_infra2;
            }
            subclass::Property("enable-color", ..) => {
                let enable_color = value.get().expect(&format!("Failed to set property `enable-color` on realsensesrc. Expected a boolean, but got: {:?}", value));
                ;
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `enable-color` from {} to {}",
                    settings.streams.enable_color,
                    enable_color
                );
                settings.streams.enable_color = enable_color;
            }
            subclass::Property("depth-width", ..) => {
                let depth_width = value.get().expect(&format!("Failed to set property `depth-width` on realsensesrc. Expected an int, but got: {:?}", value));
                ;
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
                ;
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
                ;
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
                ;
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
                ;
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
                ;
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
                ;
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
                ;
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `include-per-frame-metadata` from {} to {}",
                    settings.include_per_frame_metadata,
                    do_metadata
                );
                settings.include_per_frame_metadata = do_metadata;
            }
            subclass::Property("do-custom-timestamp", ..) => {
                let do_custom_timestamp = value.get().expect(&format!("Failed to set property `do-custom-timestamp` on realsensesrc. Expected a boolean, but got: {:?}", value));;
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `do-custom-timestamp` from {} to {}",
                    settings.do_custom_timestamp,
                    do_custom_timestamp
                );
                settings.do_custom_timestamp = do_custom_timestamp;
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
            subclass::Property("enable-depth", ..) => Ok(settings.streams.enable_depth.to_value()),
            subclass::Property("enable-infra1", ..) => {
                Ok(settings.streams.enable_infra1.to_value())
            }
            subclass::Property("enable-infra2", ..) => {
                Ok(settings.streams.enable_infra2.to_value())
            }
            subclass::Property("enable-color", ..) => Ok(settings.streams.enable_color.to_value()),
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
            subclass::Property("do-custom-timestamp", ..) => {
                Ok(settings.do_custom_timestamp.to_value())
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
        element.set_live(true);
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
        Self::check_internals(&internals)?;

        // Specify realsense log severity level
        rs2::log::log_to_console(rs2::log::rs2_log_severity::RS2_LOG_SEVERITY_ERROR);

        // Create new RealSense device config
        let config = rs2::config::Config::new().map_err(|e| {
            gst_error_msg!(
                gst::ResourceError::OpenRead,
                [format!("Could not open RealSense device: {}", e).as_str()]
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
                        [
                            format!("Failed to enable a stream on `realsensesrc`: {:?}", e)
                                .as_str()
                        ]
                    )
                })?;

                // Enable device with the given serial number and device configuration
                config.enable_device(serial.to_string()).map_err(|_e| {
                    gst_error_msg!(
                        gst::ResourceError::Settings,
                        ["No device with serial `{}` is connected!", serial]
                    )
                })?;
            }
            // A serial was not specified, but a ROSBAG was, attempt to load that instead
            None if settings.rosbag_location.is_some() => {
                let rosbag_location: &str = settings.rosbag_location.as_ref().unwrap(); // we know this always works (see match condition)
                let rosbag_location = rosbag_location.clone();
                config
                    .enable_device_from_file_repeat_option(
                        rosbag_location.to_string(),
                        settings.loop_rosbag,
                    )
                    .map_err(|e| {
                        gst_error_msg!(
                            gst::ResourceError::Settings,
                            ["Cannot read from \"{}\": {:?}!", rosbag_location, e]
                        )
                    })?;
            }
            // Neither a serial nor a ROSBAG was specified, this is a valid configuration!
            _ => {
                return Err(gst_error_msg!(
                    gst::ResourceError::Settings,
                    ["You must specify either a serial or a rosbag_location"]
                ));
            }
        }

        let pipeline = self
            .prepare_and_start_librealsense_pipeline(&config, settings)
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
        if let State::Stopped = *state {
            unreachable!("Element is not yet started");
        }
        *state = State::Stopped;

        self.parent_stop(element)
    }

    fn is_seekable(&self, _element: &gst_base::BaseSrc) -> bool {
        false
    }

    fn create(
        &self,
        _element: &gst_base::BaseSrc,
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

        // Get frames with the given timeout
        let frames = pipeline
            .wait_for_frames(settings.wait_for_frames_timeout)
            .map_err(|_| gst::FlowError::Eos)?;

        // Calculate a common `timestamp` if `do-custom-timestamp` is enabled, else set to None
        let timestamp = if settings.do_custom_timestamp {
            Some(
                std::time::SystemTime::now()
                    .duration_since(internals.system_time)
                    .unwrap_or_default()
                    .as_nanos() as u64,
            )
        } else {
            None
        };

        // Create the output buffer
        let mut output_buffer = gst::buffer::Buffer::new();

        // Attach `depth` frame if enabled
        if streams.enable_depth {
            self.extract_frame(
                &frames,
                &mut output_buffer,
                "depth",
                rs2::rs2_stream::RS2_STREAM_DEPTH,
                -1,
                &[],
                settings,
                timestamp,
            )?;
        }

        // Attach `infra1` frame if enabled
        if streams.enable_infra1 {
            self.extract_frame(
                &frames,
                &mut output_buffer,
                "infra1",
                rs2::rs2_stream::RS2_STREAM_INFRARED,
                1,
                &[streams.enable_depth],
                settings,
                timestamp,
            )?;
        }

        // Attach `infra2` frame if enabled
        if streams.enable_infra2 {
            self.extract_frame(
                &frames,
                &mut output_buffer,
                "infra2",
                rs2::rs2_stream::RS2_STREAM_INFRARED,
                2,
                &[streams.enable_depth, streams.enable_infra1],
                settings,
                timestamp,
            )?;
        }

        // Attach `color` frame if enabled
        if streams.enable_color {
            self.extract_frame(
                &frames,
                &mut output_buffer,
                "color",
                rs2::rs2_stream::RS2_STREAM_COLOR,
                -1,
                &[
                    streams.enable_depth,
                    streams.enable_infra1,
                    streams.enable_infra2,
                ],
                settings,
                timestamp,
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

            if settings.streams.enable_depth {
                // Add `depth` stream with its format, width and height into the caps if enabled
                selected_streams.push_str(&"depth,");
                s.set(
                    "depth_format",
                    &gst_video::VideoFormat::Gray16Le.to_string(),
                );
                s.set("depth_width", &settings.streams.depth_resolution.width);
                s.set("depth_height", &settings.streams.depth_resolution.height);
            }
            if settings.streams.enable_infra1 {
                // Add `infra1` stream with its format, width and height into the caps if enabled
                selected_streams.push_str(&"infra1,");
                s.set("infra1_format", &gst_video::VideoFormat::Gray8.to_string());
                s.set("infra1_width", &settings.streams.depth_resolution.width);
                s.set("infra1_height", &settings.streams.depth_resolution.height);
            }
            if settings.streams.enable_infra2 {
                // Add `infra2` stream with its format, width and height into the caps if enabled
                selected_streams.push_str(&"infra2,");
                s.set("infra2_format", &gst_video::VideoFormat::Gray8.to_string());
                s.set("infra2_width", &settings.streams.depth_resolution.width);
                s.set("infra2_height", &settings.streams.depth_resolution.height);
            }
            if settings.streams.enable_color {
                // Add `color` stream with its format, width and height into the caps if enabled
                selected_streams.push_str(&"color,");
                s.set("color_format", &gst_video::VideoFormat::Rgb.to_string());
                s.set("color_width", &settings.streams.color_resolution.width);
                s.set("color_height", &settings.streams.color_resolution.height);
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
        config: &librealsense2::config::Config,
        settings: &Settings,
    ) -> Result<rs2::pipeline::Pipeline, RealsenseError> {
        // Get context and a list of connected devices
        let context = rs2::context::Context::new()?;

        // Load JSON if `json-location` is defined
        let devices = context.get_devices()?;

        if settings.json_location.is_some() && settings.serial.is_some() {
            Self::load_json(
                &devices,
                &settings.serial.clone().unwrap(),
                &settings.json_location.clone().unwrap(),
            )?;
        }

        // Start the RealSense pipeline
        let pipeline = rs2::pipeline::Pipeline::new(&context)?;
        pipeline.start_with_config(&config)?;
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
        if !settings.streams.enable_depth
            && !settings.streams.enable_infra1
            && !settings.streams.enable_infra2
            && !settings.streams.enable_color
        {
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
        if settings.streams.enable_depth {
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
        if settings.streams.enable_infra1 {
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
        if settings.streams.enable_infra2 {
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
        if settings.streams.enable_color {
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

        device.load_json(json_content)?;
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
    fn add_per_frame_metadata(&self, buffer: &mut gst::Buffer, frame_meta: Vec<u8>, tag: &str) {
        // If we were able to read some metadata add it to the buffer
        let mut frame_meta_buffer = gst::buffer::Buffer::from_slice(frame_meta);
        let tag_name = format!("{}_meta", tag);
        let mut tags = gst::tags::TagList::new();
        tags.get_mut()
            .expect("Cannot get mutable reference to `tags`")
            .add::<gst::tags::Title>(&tag_name.as_str(), gst::TagMergeMode::Append);

        TagsMeta::add(
            frame_meta_buffer
                .get_mut()
                .expect("Could not add tags to `frame_meta_buffer`"),
            &mut tags,
        );

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
        timestamp: Option<u64>,
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

        // Add tag to this new buffer
        TagsMeta::add(
            buffer.get_mut().expect("Could not add tag to frame buffer"),
            &mut tags,
        );

        // Set timestamp
        if let Some(timestamp) = timestamp {
            buffer
                .make_mut()
                .set_pts(gst::ClockTime::from_nseconds(timestamp));
            buffer
                .make_mut()
                .set_dts(gst::ClockTime::from_nseconds(timestamp));
        };

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

        if settings.include_per_frame_metadata {
            // Attempt to read the RealSense per-frame metadata, otherwise set frame_meta to None
            let md = self.get_frame_meta(frame)?;
            self.add_per_frame_metadata(output_buffer, md, tag);
        }

        // Release the frame
        frame.release();
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
    frames.iter().find(|f| match f.get_profile() {
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
