use glib;
use glib::subclass;
use glib::subclass::prelude::*;
use gst;
use gst::prelude::*;
use gst::subclass::prelude::*;
use gst_base;
use gst_base::prelude::*;
use gst_base::subclass::prelude::*;
use meta::buffer::BufferMeta;
use meta::tags::TagsMeta;
use rs2;
use std::sync::Mutex;

const PIPELINE_WAIT_FOR_FRAMES_TIMEOUT: u32 = 500; // ms

use crate::properties_d435;
static PROPERTIES: [subclass::Property; 12] = [
    subclass::Property("serial", |name| {
        glib::ParamSpec::string(
            name,
            "Serial Number",
            "Serial number of realsense device. If unchanged or empty, `rosbag_location` is used to locate file to play from.",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("rosbag_location", |name| {
        glib::ParamSpec::string(
            name,
            "Rosbag File Location",
            "Location of the rosbag file to read from. If unchanged or empty, physical device specified by `serial` is used. If both `rosbag_location and `serial` are selected, the stream of the physical device will be recorded.",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("json_location", |name| {
        glib::ParamSpec::string(
            name,
            "JSON File Location",
            "Location of the JSON file to use that applies only if `serial` is specified. If unchanged or empty, previous JSON configuration is used. If no previous configuration is present due to hardware reset, default configuration is used.",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable_depth", |name| {
        glib::ParamSpec::boolean(
            name,
            "enable_depth",
            "Enables depth stream",
            properties_d435::DEFAULT_ENABLE_DEPTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable_infra1", |name| {
        glib::ParamSpec::boolean(
            name,
            "enable_infra1",
            "Enables infra1 stream",
            properties_d435::DEFAULT_ENABLE_INFRA1,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable_infra2", |name| {
        glib::ParamSpec::boolean(
            name,
            "enable_infra2",
            "Enables infra2 stream",
            properties_d435::DEFAULT_ENABLE_INFRA2,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable_color", |name| {
        glib::ParamSpec::boolean(
            name,
            "enable_color",
            "Enables color stream",
            properties_d435::DEFAULT_ENABLE_COLOR,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("depth_width", |name| {
        glib::ParamSpec::uint(
            name,
            "depth_width",
            "Width of the depth and IR frames",
            properties_d435::DEPTH_MIN_WIDTH,
            properties_d435::DEPTH_MAX_WIDTH,
            properties_d435::DEFAULT_DEPTH_WIDTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("depth_height", |name| {
        glib::ParamSpec::uint(
            name,
            "depth_height",
            "Height of the depth and IR frames",
            properties_d435::DEPTH_MIN_HEIGHT,
            properties_d435::DEPTH_MAX_HEIGHT,
            properties_d435::DEFAULT_DEPTH_HEIGHT,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color_width", |name| {
        glib::ParamSpec::uint(
            name,
            "color_width",
            "Width of the color frame",
            properties_d435::COLOR_MIN_WIDTH,
            properties_d435::COLOR_MAX_WIDTH,
            properties_d435::DEFAULT_COLOR_WIDTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color_height", |name| {
        glib::ParamSpec::uint(
            name,
            "color_height",
            "Height of the color frame",
            properties_d435::COLOR_MIN_HEIGHT,
            properties_d435::COLOR_MAX_HEIGHT,
            properties_d435::DEFAULT_COLOR_HEIGHT,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("framerate", |name| {
        glib::ParamSpec::uint(
            name,
            "framerate",
            "Framerate of the stream",
            properties_d435::MIN_FRAMERATE,
            properties_d435::MAX_FRAMERATE,
            properties_d435::DEFAULT_FRAMERATE,
            glib::ParamFlags::READWRITE,
        )
    }),
];

struct Settings {
    serial: Option<String>,
    rosbag_location: Option<String>,
    json_location: Option<String>,
    streams: Streams,
}

struct Streams {
    enable_depth: bool,
    enable_infra1: bool,
    enable_infra2: bool,
    enable_color: bool,
    depth_resolution: StreamResolution,
    color_resolution: StreamResolution,
    framerate: u32,
}

struct StreamResolution {
    width: u32,
    height: u32,
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
        }
    }
}

enum State {
    Stopped,
    Started { pipeline: rs2::pipeline::Pipeline },
}

impl Default for State {
    fn default() -> State {
        State::Stopped
    }
}

pub struct RealsenseSrc {
    cat: gst::DebugCategory,
    settings: Mutex<Settings>,
    state: Mutex<State>,
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
            settings: Mutex::new(Settings::default()),
            state: Mutex::new(State::default()),
        }
    }

    fn class_init(klass: &mut subclass::simple::ClassStruct<Self>) {
        klass.set_metadata(
            "Realsense Source",
            "Source/RGB-D/Realsense",
            "Stream `video/rgbd` from a RealSense device",
            "Niclas Moeslund Overby <noverby@prozum.dk>",
        );

        let caps = gst::Caps::new_simple(
            "video/rgbd",
            &[
                // List of the available streams
                ("streams", &"depth,infra1,infra2,color"),
                (
                    "framerate",
                    &gst::FractionRange::new(
                        gst::Fraction::new(properties_d435::MIN_FRAMERATE as i32, 1),
                        gst::Fraction::new(properties_d435::MAX_FRAMERATE as i32, 1),
                    ),
                ),
            ],
        );

        let src_pad_template = gst::PadTemplate::new(
            "src",
            gst::PadDirection::Src,
            gst::PadPresence::Always,
            &caps,
        )
        .unwrap();

        klass.add_pad_template(src_pad_template);

        klass.install_properties(&PROPERTIES);
    }
}

impl ObjectImpl for RealsenseSrc {
    glib_object_impl!();

    fn set_property(&self, obj: &glib::Object, id: usize, value: &glib::Value) {
        let element = obj.downcast_ref::<gst_base::BaseSrc>().unwrap();
        let property = &PROPERTIES[id];
        let mut settings = self.settings.lock().unwrap();

        match *property {
            subclass::Property("serial", ..) => {
                settings.serial = match value.get::<String>() {
                    Some(serial) => {
                        if serial.is_empty() {
                            None
                        } else {
                            gst_info!(
                                self.cat,
                                obj: element,
                                "Changing property `serial` to {}",
                                serial
                            );
                            Some(serial)
                        }
                    }
                    None => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `serial` to `None`"
                        );
                        None
                    }
                };
            }
            subclass::Property("rosbag_location", ..) => {
                settings.rosbag_location = match value.get::<String>() {
                    Some(rosbag_location) => {
                        if rosbag_location.is_empty() {
                            None
                        } else {
                            gst_info!(
                                self.cat,
                                obj: element,
                                "Changing property `rosbag_location` to {}",
                                rosbag_location
                            );
                            Some(rosbag_location)
                        }
                    }
                    None => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `rosbag_location` to `None`"
                        );
                        None
                    }
                };
            }
            subclass::Property("json_location", ..) => {
                settings.json_location = match value.get::<String>() {
                    Some(json_location) => {
                        if json_location.is_empty() {
                            None
                        } else {
                            gst_info!(
                                self.cat,
                                obj: element,
                                "Changing property `json_location` to {}",
                                json_location
                            );
                            Some(json_location)
                        }
                    }
                    None => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `json_location` to `None`"
                        );
                        None
                    }
                };
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
            _ => unimplemented!("Property is not implemented"),
        };
    }

    fn get_property(&self, _obj: &glib::Object, id: usize) -> Result<glib::Value, ()> {
        let prop = &PROPERTIES[id];
        let settings = &self.settings.lock().unwrap();
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
        let mut state = self.state.lock().unwrap();
        if let State::Started { .. } = *state {
            unreachable!("Element realsensesrc has already started");
        }

        let settings = self.settings.lock().unwrap();

        if settings.rosbag_location == None && settings.serial == None {
            gst_error!(
                self.cat,
                obj: element,
                "Neither the `serial` or `rosbag_location` properties are defined. At least one of these must be defined!"
            );
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
            gst_error!(
                self.cat,
                obj: element,
                "No stream is enabled. At least one stream must be enabled!"
            );
            return Err(gst_error_msg!(
                gst::ResourceError::Settings,
                ["No stream is enabled. At least one stream must be enabled!"]
            ));
        }

        rs2::log::log_to_console(rs2::log::rs2_log_severity::RS2_LOG_SEVERITY_ERROR);
        let config = rs2::config::Config::new().unwrap();

        if let Some(serial) = settings.serial.as_ref() {
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
                        settings.streams.depth_resolution.width as i32,
                        settings.streams.depth_resolution.height as i32,
                        rs2::rs2_format::RS2_FORMAT_Z16,
                        settings.streams.framerate as i32,
                    )
                    .unwrap();
            }
            if settings.streams.enable_infra1 {
                config
                    .enable_stream(
                        rs2::rs2_stream::RS2_STREAM_INFRARED,
                        1,
                        settings.streams.depth_resolution.width as i32,
                        settings.streams.depth_resolution.height as i32,
                        rs2::rs2_format::RS2_FORMAT_Y8,
                        settings.streams.framerate as i32,
                    )
                    .unwrap();
            }
            if settings.streams.enable_infra2 {
                config
                    .enable_stream(
                        rs2::rs2_stream::RS2_STREAM_INFRARED,
                        2,
                        settings.streams.depth_resolution.width as i32,
                        settings.streams.depth_resolution.height as i32,
                        rs2::rs2_format::RS2_FORMAT_Y8,
                        settings.streams.framerate as i32,
                    )
                    .unwrap();
            }
            if settings.streams.enable_color {
                config
                    .enable_stream(
                        rs2::rs2_stream::RS2_STREAM_COLOR,
                        -1,
                        settings.streams.color_resolution.width as i32,
                        settings.streams.color_resolution.height as i32,
                        rs2::rs2_format::RS2_FORMAT_RGB8,
                        settings.streams.framerate as i32,
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

        let context = rs2::context::Context::new().unwrap();
        let devices = context.get_devices().unwrap();

        // Make sure the selected serial is connected
        if let Some(serial) = settings.serial.as_ref() {
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
            if !found_matching_serial {
                gst_error!(
                    self.cat,
                    obj: element,
                    "No device with serial `{}` is detected",
                    serial
                );
                return Err(gst_error_msg!(
                    gst::ResourceError::Settings,
                    [&format!("No device with serial `{}` is detected", serial)]
                ));
            }

            // Load JSON file
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

        let pipeline = rs2::pipeline::Pipeline::new(&context).unwrap();
        pipeline.start_with_config(&config).unwrap();
        *state = State::Started { pipeline };

        gst_info!(self.cat, obj: element, "Started");

        Ok(())
    }

    fn stop(&self, element: &gst_base::BaseSrc) -> Result<(), gst::ErrorMessage> {
        let mut state = self.state.lock().unwrap();
        if let State::Stopped = *state {
            unreachable!("realsensesrc is not yet started");
        }

        *state = State::Stopped;

        gst_info!(self.cat, obj: element, "Stopped");

        Ok(())
    }

    fn fixate(&self, element: &gst_base::BaseSrc, caps: gst::Caps) -> gst::Caps {
        let settings = self.settings.lock().unwrap();
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

            // Pop the last ',' contained in streams
            selected_streams.pop();

            // Finally add the streams to the caps
            s.set("streams", &selected_streams.as_str());

            // Fixate the framerate
            s.fixate_field_nearest_fraction("framerate", settings.streams.framerate as i32);
        }
        self.parent_fixate(element, caps)
    }

    fn is_seekable(&self, _element: &gst_base::BaseSrc) -> bool {
        false
    }

    fn create(
        &self,
        element: &gst_base::BaseSrc,
        _: u64,
        _: u32,
    ) -> Result<gst::Buffer, gst::FlowError> {
        let settings = self.settings.lock().unwrap();
        let mut state = self.state.lock().unwrap();
        let pipeline = match *state {
            State::Started { ref mut pipeline } => pipeline,
            State::Stopped => {
                gst_error!(self.cat, obj: element, "Pipeline is not yet started");
                return Err(gst::FlowError::Error);
            }
        };

        // Get frames
        let frames = pipeline
            .wait_for_frames(PIPELINE_WAIT_FOR_FRAMES_TIMEOUT)
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
    //                 .mul_div_floor(1, settings.streams.framerate.into())
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
