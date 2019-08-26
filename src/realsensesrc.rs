use glib::subclass;
use gst::subclass::prelude::*;
use gst_base::prelude::*;
use gst_base::subclass::prelude::*;
use gst_depth_meta::buffer::BufferMeta;
use gst_depth_meta::tags::TagsMeta;
use rs2;
use std::sync::Mutex;

// Default timeout used while waiting for frames from a realsense device in milliseconds.
const DEFAULT_PIPELINE_WAIT_FOR_FRAMES_TIMEOUT: u32 = 500;

use crate::properties_d435;
static PROPERTIES: [subclass::Property; 13] = [
    subclass::Property("serial", |name| {
        glib::ParamSpec::string(
            name,
            "Serial Number",
            "Serial number of a realsense device. If unchanged or empty, `rosbag_location` is used to locate a file to play from.",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("rosbag_location", |name| {
        glib::ParamSpec::string(
            name,
            "Rosbag File Location",
            "Location of a rosbag file to play from. If unchanged or empty, physical device specified by `serial` is used. If both `serial` and `rosbag_location` are selected, the selected streams are recorded into a file specified by this property.",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("json_location", |name| {
        glib::ParamSpec::string(
            name,
            "JSON File Location",
            "Location of a JSON file to load the RealSense device configuration from. This property applies only if `serial` is specified. If unchanged or empty, previous JSON configuration is used. If no previous configuration is present due to hardware reset, default configuration is used.",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable_depth", |name| {
        glib::ParamSpec::boolean(
            name,
            "enable_depth",
            "Enables depth stream.",
            properties_d435::DEFAULT_ENABLE_DEPTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable_infra1", |name| {
        glib::ParamSpec::boolean(
            name,
            "enable_infra1",
            "Enables infra1 stream.",
            properties_d435::DEFAULT_ENABLE_INFRA1,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable_infra2", |name| {
        glib::ParamSpec::boolean(
            name,
            "enable_infra2",
            "Enables infra2 stream.",
            properties_d435::DEFAULT_ENABLE_INFRA2,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable_color", |name| {
        glib::ParamSpec::boolean(
            name,
            "enable_color",
            "Enables color stream.",
            properties_d435::DEFAULT_ENABLE_COLOR,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("depth_width", |name| {
        glib::ParamSpec::int(
            name,
            "depth_width",
            "Width of the depth and IR frames.",
            properties_d435::DEPTH_MIN_WIDTH,
            properties_d435::DEPTH_MAX_WIDTH,
            properties_d435::DEFAULT_DEPTH_WIDTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("depth_height", |name| {
        glib::ParamSpec::int(
            name,
            "depth_height",
            "Height of the depth and IR frames.",
            properties_d435::DEPTH_MIN_HEIGHT,
            properties_d435::DEPTH_MAX_HEIGHT,
            properties_d435::DEFAULT_DEPTH_HEIGHT,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color_width", |name| {
        glib::ParamSpec::int(
            name,
            "color_width",
            "Width of the color frame.",
            properties_d435::COLOR_MIN_WIDTH,
            properties_d435::COLOR_MAX_WIDTH,
            properties_d435::DEFAULT_COLOR_WIDTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color_height", |name| {
        glib::ParamSpec::int(
            name,
            "color_height",
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
            "framerate",
            "Common framerate of the selected streams.",
            properties_d435::MIN_FRAMERATE,
            properties_d435::MAX_FRAMERATE,
            properties_d435::DEFAULT_FRAMERATE,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("wait_for_frames_timeout", |name| {
        glib::ParamSpec::uint(
            name,
            "wait_for_frames_timeout",
            "Timeout used while waiting for frames from a RealSense device in milliseconds",
            std::u32::MIN,
            std::u32::MAX,
            DEFAULT_PIPELINE_WAIT_FOR_FRAMES_TIMEOUT,
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
    wait_for_frames_timeout: u32,
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
            wait_for_frames_timeout: DEFAULT_PIPELINE_WAIT_FOR_FRAMES_TIMEOUT,
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
}

impl ObjectSubclass for RealsenseSrc {
    const NAME: &'static str = "realsensesrc";
    type ParentType = gst_base::BaseSrc;
    type Instance = gst::subclass::ElementInstanceStruct<Self>;
    type Class = subclass::simple::ClassStruct<Self>;

    glib_object_subclass!();

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
            }),
        }
    }

    fn class_init(klass: &mut subclass::simple::ClassStruct<Self>) {
        klass.set_metadata(
            "Realsense Source",
            "Source/RGB-D/Realsense",
            "Stream `video/rgbd` from a RealSense device",
            "Niclas Moeslund Overby <niclas.overby@aivero.com>, Andrej Orsula <andrej.orsula@aivero.com>",
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
            .unwrap(),
        );
    }
}

impl ObjectImpl for RealsenseSrc {
    glib_object_impl!();

    fn set_property(&self, obj: &glib::Object, id: usize, value: &glib::Value) {
        let element = obj.downcast_ref::<gst_base::BaseSrc>().unwrap();
        let settings = &mut self.internals.lock().unwrap().settings;

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
            subclass::Property("rosbag_location", ..) => {
                let rosbag_location = value.get::<String>();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `rosbag_location` from {:?} to {:?}",
                    settings.rosbag_location,
                    rosbag_location
                );
                settings.rosbag_location = rosbag_location;
            }
            subclass::Property("json_location", ..) => {
                let json_location = value.get::<String>();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `json_location` from {:?} to {:?}",
                    settings.json_location,
                    json_location
                );
                settings.json_location = json_location;
            }
            subclass::Property("enable_depth", ..) => {
                let enable_depth = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `enable_depth` from {} to {}",
                    settings.streams.enable_depth,
                    enable_depth
                );
                settings.streams.enable_depth = enable_depth;
            }
            subclass::Property("enable_infra1", ..) => {
                let enable_infra1 = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `enable_infra1` from {} to {}",
                    settings.streams.enable_infra1,
                    enable_infra1
                );
                settings.streams.enable_infra1 = enable_infra1;
            }
            subclass::Property("enable_infra2", ..) => {
                let enable_infra2 = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `enable_infra2` from {} to {}",
                    settings.streams.enable_infra2,
                    enable_infra2
                );
                settings.streams.enable_infra2 = enable_infra2;
            }
            subclass::Property("enable_color", ..) => {
                let enable_color = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `enable_color` from {} to {}",
                    settings.streams.enable_color,
                    enable_color
                );
                settings.streams.enable_color = enable_color;
            }
            subclass::Property("depth_width", ..) => {
                let depth_width = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `depth_width` from {} to {}",
                    settings.streams.depth_resolution.width,
                    depth_width
                );
                settings.streams.depth_resolution.width = depth_width;
            }
            subclass::Property("depth_height", ..) => {
                let depth_height = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `depth_height` from {} to {}",
                    settings.streams.depth_resolution.height,
                    depth_height
                );
                settings.streams.depth_resolution.height = depth_height;
            }
            subclass::Property("color_width", ..) => {
                let color_width = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `color_width` from {} to {}",
                    settings.streams.color_resolution.width,
                    color_width
                );
                settings.streams.color_resolution.width = color_width;
            }
            subclass::Property("color_height", ..) => {
                let color_height = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `color_height` from {} to {}",
                    settings.streams.color_resolution.height,
                    color_height
                );
                settings.streams.color_resolution.height = color_height;
            }
            subclass::Property("framerate", ..) => {
                let framerate = value.get().unwrap();
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
            subclass::Property("wait_for_frames_timeout", ..) => {
                let wait_for_frames_timeout = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `wait_for_frames_timeout` from {} to {}",
                    settings.wait_for_frames_timeout,
                    wait_for_frames_timeout
                );
                settings.wait_for_frames_timeout = wait_for_frames_timeout;
            }
            _ => unimplemented!("Property is not implemented"),
        };
    }

    fn get_property(&self, _obj: &glib::Object, id: usize) -> Result<glib::Value, ()> {
        let settings = &self.internals.lock().unwrap().settings;

        let prop = &PROPERTIES[id];
        match *prop {
            subclass::Property("serial", ..) => {
                let serial = settings
                    .serial
                    .as_ref()
                    .map(|rosbag_location| rosbag_location.to_string());
                Ok(serial.to_value())
            }
            subclass::Property("rosbag_location", ..) => {
                let rosbag_location = settings
                    .rosbag_location
                    .as_ref()
                    .map(|rosbag_location| rosbag_location.to_string());
                Ok(rosbag_location.to_value())
            }
            subclass::Property("json_location", ..) => {
                let json_location = settings
                    .json_location
                    .as_ref()
                    .map(|json_location| json_location.to_string());
                Ok(json_location.to_value())
            }
            subclass::Property("enable_depth", ..) => Ok(settings.streams.enable_depth.to_value()),
            subclass::Property("enable_infra1", ..) => {
                Ok(settings.streams.enable_infra1.to_value())
            }
            subclass::Property("enable_infra2", ..) => {
                Ok(settings.streams.enable_infra2.to_value())
            }
            subclass::Property("enable_color", ..) => Ok(settings.streams.enable_color.to_value()),
            subclass::Property("depth_width", ..) => {
                Ok(settings.streams.depth_resolution.width.to_value())
            }
            subclass::Property("depth_height", ..) => {
                Ok(settings.streams.depth_resolution.height.to_value())
            }
            subclass::Property("color_width", ..) => {
                Ok(settings.streams.color_resolution.width.to_value())
            }
            subclass::Property("color_height", ..) => {
                Ok(settings.streams.color_resolution.height.to_value())
            }
            subclass::Property("framerate", ..) => Ok(settings.streams.framerate.to_value()),
            subclass::Property("wait_for_frames_timeout", ..) => {
                Ok(settings.wait_for_frames_timeout.to_value())
            }
            _ => unimplemented!("Property is not implemented"),
        }
    }

    fn constructed(&self, obj: &glib::Object) {
        self.parent_constructed(obj);

        let element = obj.downcast_ref::<gst_base::BaseSrc>().unwrap();
        element.set_format(gst::Format::Time);
        element.set_live(true);
    }
}

impl ElementImpl for RealsenseSrc {}

impl BaseSrcImpl for RealsenseSrc {
    fn start(&self, element: &gst_base::BaseSrc) -> Result<(), gst::ErrorMessage> {
        let internals = &mut self.internals.lock().unwrap();
        if let State::Started { .. } = internals.state {
            unreachable!("Element has already started");
        }

        let settings = &internals.settings;

        if settings.rosbag_location == None && settings.serial == None {
            return Err(gst_error_msg!(
                gst::ResourceError::Settings,
                ["Neither the `serial` or `rosbag_location` properties are defined. At least one of these must be defined!"]
            ));
        }

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

        rs2::log::log_to_console(rs2::log::rs2_log_severity::RS2_LOG_SEVERITY_ERROR);
        let config = rs2::config::Config::new().unwrap();

        // Based on properties, enable streaming, reading from or recording to a file (with the enabled streams)
        if let Some(serial) = &settings.serial {
            if let Some(rosbag_location) = settings.rosbag_location.as_ref() {
                config
                    .enable_record_to_file(rosbag_location.to_string())
                    .unwrap();
            };

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
                    .unwrap();
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
                    .unwrap();
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
                    .unwrap();
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
                    .unwrap();
            }

            config.enable_device(serial.to_string()).unwrap();
        } else {
            if let Some(rosbag_location) = settings.rosbag_location.as_ref() {
                config
                    .enable_device_from_file_repeat_option(rosbag_location.to_string(), true)
                    .unwrap();
            };
        }

        // Get context and a list of connected devices
        let context = rs2::context::Context::new().unwrap();
        let devices = context.get_devices().unwrap();

        // Make sure a device with the selected serial is connected
        if let Some(serial) = settings.serial.as_ref() {
            // Get the index of the matching device
            let mut index_of_used_device: usize = 0;
            let mut found_matching_serial = false;
            for device in devices.iter() {
                let serial_number = device
                    .get_info(rs2::rs2_camera_info::RS2_CAMERA_INFO_SERIAL_NUMBER)
                    .unwrap();
                if *serial == serial_number {
                    found_matching_serial = true;
                    break;
                }
                index_of_used_device += 1;
            }

            // Return error if there is no such device
            if !found_matching_serial {
                return Err(gst_error_msg!(
                    gst::ResourceError::Settings,
                    [&format!("No device with serial `{}` is detected", serial)]
                ));
            }

            // Load JSON file if specified
            if let Some(json_location) = settings.json_location.as_ref() {
                if !devices[index_of_used_device]
                    .is_advanced_mode_enabled()
                    .unwrap()
                {
                    devices[index_of_used_device]
                        .set_advanced_mode(true)
                        .unwrap();
                }
                let json_content = std::fs::read_to_string(json_location).unwrap();
                devices[index_of_used_device]
                    .load_json(json_content)
                    .unwrap();
            }
        }

        // Start the RealSense pipeline
        let pipeline = rs2::pipeline::Pipeline::new(&context).unwrap();
        pipeline.start_with_config(&config).unwrap();
        internals.state = State::Started { pipeline };

        gst_info!(self.cat, obj: element, "Streaming started");
        Ok(())
    }

    fn stop(&self, element: &gst_base::BaseSrc) -> Result<(), gst::ErrorMessage> {
        let state = &mut self.internals.lock().unwrap().state;
        if let State::Stopped = *state {
            unreachable!("Element is not yet started");
        }
        *state = State::Stopped;

        gst_info!(self.cat, obj: element, "Stopped");
        Ok(())
    }

    fn fixate(&self, element: &gst_base::BaseSrc, caps: gst::Caps) -> gst::Caps {
        let settings = &self.internals.lock().unwrap().settings;

        let mut caps = gst::Caps::truncate(caps);
        {
            let caps = caps.make_mut();
            let s = caps.get_mut_structure(0).unwrap();

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

    fn is_seekable(&self, _element: &gst_base::BaseSrc) -> bool {
        false
    }

    fn create(
        &self,
        _element: &gst_base::BaseSrc,
        _offset: u64,
        _length: u32,
    ) -> Result<gst::Buffer, gst::FlowError> {
        let intenals = &mut *self.internals.lock().unwrap();
        let settings = &intenals.settings;

        // Get the RealSense pipeline
        let pipeline = match intenals.state {
            State::Started { ref pipeline } => pipeline,
            State::Stopped => {
                unreachable!("Element is not yet started");
            }
        };

        // Get frames with the given timeout
        let frames = pipeline
            .wait_for_frames(settings.wait_for_frames_timeout)
            .unwrap();

        // Create the output buffer
        let mut output_buffer = gst::buffer::Buffer::new();

        // Attach depth frame if enabled
        if settings.streams.enable_depth {
            // Extract the frame
            let depth_frame = frames
                .iter()
                .find(|f| {
                    f.get_profile().unwrap().get_data().unwrap().stream
                        == rs2::rs2_stream::RS2_STREAM_DEPTH
                })
                .unwrap();
            // Put this frame into the output buffer
            output_buffer = gst::buffer::Buffer::from_mut_slice(depth_frame.get_data().unwrap());
            // Release the frame
            depth_frame.release();
            // Add the appropriate tag
            let mut depth_tags = gst::tags::TagList::new();
            depth_tags
                .get_mut()
                .unwrap()
                .add::<gst::tags::Title>(&"depth", gst::TagMergeMode::Append);
            TagsMeta::add(output_buffer.get_mut().unwrap(), &mut depth_tags);
        }

        // Attach infra1 frame if enabled
        if settings.streams.enable_infra1 {
            // Extract the frame
            let infra1_frame = frames
                .iter()
                .find(|f| {
                    f.get_profile().unwrap().get_data().unwrap().stream
                        == rs2::rs2_stream::RS2_STREAM_INFRARED
                        && f.get_profile().unwrap().get_data().unwrap().index == 1
                })
                .unwrap();
            // Create the appropriate tag
            let mut infra1_tags = gst::tags::TagList::new();
            infra1_tags
                .get_mut()
                .unwrap()
                .add::<gst::tags::Title>(&"infra1", gst::TagMergeMode::Append);
            if settings.streams.enable_depth {
                // If any of the previous streams are enabled, simply put the frame in a new buffer and attach it as meta
                let mut infra1_buffer =
                    gst::buffer::Buffer::from_mut_slice(infra1_frame.get_data().unwrap());
                // Add tag to this new buffer
                TagsMeta::add(infra1_buffer.get_mut().unwrap(), &mut infra1_tags);
                // Attach this new buffer as meta to the output buffer
                BufferMeta::add(output_buffer.get_mut().unwrap(), &mut infra1_buffer);
            } else {
                // Else put this frame into the output buffer
                output_buffer =
                    gst::buffer::Buffer::from_mut_slice(infra1_frame.get_data().unwrap());
                // Add the tag
                TagsMeta::add(output_buffer.get_mut().unwrap(), &mut infra1_tags);
            }
            // Release the frame
            infra1_frame.release();
        }

        // Attach infra2 frame if enabled
        if settings.streams.enable_infra2 {
            // Extract the frame
            let infra2_frame = frames
                .iter()
                .find(|f| {
                    f.get_profile().unwrap().get_data().unwrap().stream
                        == rs2::rs2_stream::RS2_STREAM_INFRARED
                        && f.get_profile().unwrap().get_data().unwrap().index == 2
                })
                .unwrap();
            // Create the appropriate tag
            let mut infra2_tags = gst::tags::TagList::new();
            infra2_tags
                .get_mut()
                .unwrap()
                .add::<gst::tags::Title>(&"infra2", gst::TagMergeMode::Append);
            if settings.streams.enable_depth || settings.streams.enable_infra1 {
                // If any of the previous streams are enabled, simply put the frame in a new buffer and attach it as meta
                let mut infra2_buffer =
                    gst::buffer::Buffer::from_mut_slice(infra2_frame.get_data().unwrap());
                // Add tag to this new buffer
                TagsMeta::add(infra2_buffer.get_mut().unwrap(), &mut infra2_tags);
                // Attach this new buffer as meta to the output buffer
                BufferMeta::add(output_buffer.get_mut().unwrap(), &mut infra2_buffer);
            } else {
                // Else put this frame into the output buffer
                output_buffer =
                    gst::buffer::Buffer::from_mut_slice(infra2_frame.get_data().unwrap());
                // Add the tag
                TagsMeta::add(output_buffer.get_mut().unwrap(), &mut infra2_tags);
            }
            // Release the frame
            infra2_frame.release();
        }

        // Attach color frame if enabled
        if settings.streams.enable_color {
            // Extract the frame
            let color_frame = frames
                .iter()
                .find(|f| {
                    f.get_profile().unwrap().get_data().unwrap().stream
                        == rs2::rs2_stream::RS2_STREAM_COLOR
                })
                .unwrap();
            // Create the appropriate tag
            let mut color_tags = gst::tags::TagList::new();
            color_tags
                .get_mut()
                .unwrap()
                .add::<gst::tags::Title>(&"color", gst::TagMergeMode::Append);
            if settings.streams.enable_depth
                || settings.streams.enable_infra1
                || settings.streams.enable_infra2
            {
                // If any of the previous streams are enabled, simply put the frame in a new buffer and attach it as meta
                let mut color_buffer =
                    gst::buffer::Buffer::from_mut_slice(color_frame.get_data().unwrap());
                // Add tag to this new buffer
                TagsMeta::add(color_buffer.get_mut().unwrap(), &mut color_tags);
                // Attach this new buffer as meta to the output buffer
                BufferMeta::add(output_buffer.get_mut().unwrap(), &mut color_buffer);
            } else {
                // Else put this frame into the output buffer
                output_buffer =
                    gst::buffer::Buffer::from_mut_slice(color_frame.get_data().unwrap());
                // Add the tag
                TagsMeta::add(output_buffer.get_mut().unwrap(), &mut color_tags);
            }
            // Release the frame
            color_frame.release();
        }

        Ok(output_buffer)
    }

    // fn query(&self, element: &gst_base::BaseSrc, query: &mut gst::QueryRef) -> bool {
    //     use gst::QueryView;

    //     match query.view_mut() {
    //         QueryView::Scheduling(ref mut q) => {
    //             q.set(gst::SchedulingFlags::SEQUENTIAL, 1, -1, 0);
    //             q.add_scheduling_modes(&[gst::PadMode::Push]);
    //             true
    //         }
    //         QueryView::Latency(ref mut q) => {
    //             // TODO: Determine the actual latency caused by system buffering and gstreamer copying
    //             let settings = self.settings.lock().unwrap();
    //             let latency = gst::SECOND
    //                 .mul_div_floor(1, settings.streams.framerate as u64)
    //                 .unwrap();
    //             gst_debug!(self.cat, obj: element, "Returning latency {}", latency);
    //             q.set(true, latency, gst::CLOCK_TIME_NONE);
    //             true
    //         }
    //         _ => BaseSrcImplExt::parent_query(self, element, query),
    //     }
    // }
}

pub fn register(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    gst::Element::register(
        Some(plugin),
        "realsensesrc",
        gst::Rank::None,
        RealsenseSrc::get_type(),
    )
}
