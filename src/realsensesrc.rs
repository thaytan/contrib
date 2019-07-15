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

use std::sync::Mutex;

use rs2;

use crate::properties;
static PROPERTIES: [subclass::Property; 10] = [
    subclass::Property("location", |name| {
        glib::ParamSpec::string(
            name,
            "File Location",
            "Location of the file to read from",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("serial", |name| {
        glib::ParamSpec::string(
            name,
            "Serial Number",
            "Serial number of realsense device",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("framerate", |name| {
        glib::ParamSpec::uint(
            name,
            "framerate",
            "Framerate of the stream",
            properties::MIN_FRAMERATE,
            properties::MAX_FRAMERATE,
            properties::DEFAULT_FRAMERATE,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("depth_width", |name| {
        glib::ParamSpec::uint(
            name,
            "depth_width",
            "Width of the depth and IR frames",
            properties::DEPTH_MIN_WIDTH,
            properties::DEPTH_MAX_WIDTH,
            properties::DEFAULT_DEPTH_WIDTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("depth_height", |name| {
        glib::ParamSpec::uint(
            name,
            "depth_height",
            "Height of the depth and IR frames",
            properties::DEPTH_MIN_HEIGHT,
            properties::DEPTH_MAX_HEIGHT,
            properties::DEFAULT_DEPTH_HEIGHT,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable_color", |name| {
        glib::ParamSpec::boolean(
            name,
            "enable_color",
            "Enables color stream",
            properties::DEFAULT_ENABLE_COLOR,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color_width", |name| {
        glib::ParamSpec::uint(
            name,
            "color_width",
            "Width of the color frame",
            properties::COLOR_MIN_WIDTH,
            properties::COLOR_MAX_WIDTH,
            properties::DEFAULT_COLOR_WIDTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color_height", |name| {
        glib::ParamSpec::uint(
            name,
            "color_height",
            "Height of the color frame",
            properties::COLOR_MIN_HEIGHT,
            properties::COLOR_MAX_HEIGHT,
            properties::DEFAULT_COLOR_HEIGHT,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable_infra1", |name| {
        glib::ParamSpec::boolean(
            name,
            "enable_infra1",
            "Enables infra1 stream",
            properties::DEFAULT_ENABLE_INFRA_1,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable_infra2", |name| {
        glib::ParamSpec::boolean(
            name,
            "enable_infra2",
            "Enables infra2 stream",
            properties::DEFAULT_ENABLE_INFRA_2,
            glib::ParamFlags::READWRITE,
        )
    }),
];

enum State {
    Stopped,
    Started { pipeline: rs2::pipeline::Pipeline },
}

impl Default for State {
    fn default() -> State {
        State::Stopped
    }
}

struct Settings {
    location: Option<String>,
    serial: Option<String>,
    framerate: u32,
    depth: FrameResolution,
    color: OptionalStream,
    infra: (bool, bool),
}

impl Default for Settings {
    fn default() -> Self {
        Settings {
            location: None,
            serial: None,
            framerate: properties::DEFAULT_FRAMERATE,
            depth: FrameResolution::new(
                properties::DEFAULT_DEPTH_WIDTH,
                properties::DEFAULT_DEPTH_HEIGHT,
            ),
            color: OptionalStream::new(
                properties::DEFAULT_ENABLE_COLOR,
                properties::DEFAULT_COLOR_WIDTH,
                properties::DEFAULT_COLOR_HEIGHT,
            ),
            infra: (
                properties::DEFAULT_ENABLE_INFRA_1,
                properties::DEFAULT_ENABLE_INFRA_2,
            ),
        }
    }
}

struct FrameResolution {
    width: u32,
    height: u32,
}

impl FrameResolution {
    fn new(width: u32, height: u32) -> Self {
        FrameResolution {
            width: width,
            height: height,
        }
    }
}

struct OptionalStream {
    enabled: bool,
    resolution: FrameResolution,
}

impl OptionalStream {
    fn new(enable: bool, width: u32, height: u32) -> Self {
        OptionalStream {
            enabled: enable,
            resolution: FrameResolution::new(width, height),
        }
    }
}

pub struct RealsenseSrc {
    cat: gst::DebugCategory,
    settings: Mutex<Settings>,
    state: Mutex<State>,
}

impl RealsenseSrc {}

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
            settings: Mutex::new(Default::default()),
            state: Mutex::new(Default::default()),
        }
    }

    fn class_init(klass: &mut subclass::simple::ClassStruct<Self>) {
        klass.set_metadata(
            "Realsense Source",
            "Source/Realsense",
            "Read stream from a Realsense device or file",
            "Niclas Moeslund Overby <noverby@prozum.dk>",
        );

        let caps = gst::Caps::new_simple(
            "video/x-raw",
            &[
                ("format", &"GRAY16_LE"),
                (
                    "width",
                    &gst::IntRange::<i32>::new(
                        properties::DEPTH_MIN_WIDTH as i32,
                        properties::DEPTH_MAX_WIDTH as i32,
                    ),
                ),
                (
                    "height",
                    &gst::IntRange::<i32>::new(
                        properties::DEPTH_MIN_HEIGHT as i32,
                        properties::DEPTH_MAX_HEIGHT as i32,
                    ),
                ),
                (
                    "framerate",
                    &gst::FractionRange::new(
                        gst::Fraction::new(properties::MIN_FRAMERATE as i32, 1),
                        gst::Fraction::new(properties::MAX_FRAMERATE as i32, 1),
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
        if let State::Started { .. } = *self.state.lock().unwrap() {
            gst_error!(
                self.cat,
                obj: element,
                "Changing a property on a started `realsensesrc` is not supported"
            );
            return;
        }

        let property = &PROPERTIES[id];
        let mut settings = self.settings.lock().unwrap();

        match *property {
            subclass::Property("location", ..) => {
                settings.location = match value.get::<String>() {
                    Some(location) => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `location` to {}",
                            location
                        );
                        (Some(location))
                    }
                    None => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `location` to `None`"
                        );
                        None
                    }
                };
            }
            subclass::Property("serial", ..) => {
                settings.serial = match value.get::<String>() {
                    Some(serial) => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `serial` to {}",
                            serial
                        );
                        (Some(serial))
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
            subclass::Property("framerate", ..) => {
                let framerate = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `framerate` from {} to {}",
                    settings.framerate,
                    framerate
                );
                settings.framerate = framerate;
            }
            subclass::Property("depth_width", ..) => {
                let depth_width = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `depth_width` from {} to {}",
                    settings.depth.width,
                    depth_width
                );
                settings.depth.width = depth_width;
            }
            subclass::Property("depth_height", ..) => {
                let depth_height = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `depth_height` from {} to {}",
                    settings.depth.height,
                    depth_height
                );
                settings.depth.height = depth_height;
            }
            subclass::Property("enable_color", ..) => {
                let enable_color = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `enable_color` from {} to {}",
                    settings.color.enabled,
                    enable_color
                );
                settings.color.enabled = enable_color;
            }
            subclass::Property("color_width", ..) => {
                let color_width = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `color_width` from {} to {}",
                    settings.color.resolution.width,
                    color_width
                );
                settings.color.resolution.width = color_width;
            }
            subclass::Property("color_height", ..) => {
                let color_height = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `color_height` from {} to {}",
                    settings.color.resolution.height,
                    color_height
                );
                settings.color.resolution.height = color_height;
            }
            subclass::Property("enable_infra1", ..) => {
                let enable_infra1 = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `enable_infra1` from {} to {}",
                    settings.infra.0,
                    enable_infra1
                );
                settings.infra.0 = enable_infra1;
            }
            subclass::Property("enable_infra2", ..) => {
                let enable_infra2 = value.get().unwrap();
                gst_info!(
                    self.cat,
                    obj: element,
                    "Changing property `enable_infra2` from {} to {}",
                    settings.infra.1,
                    enable_infra2
                );
                settings.infra.1 = enable_infra2;
            }
            _ => unimplemented!(),
        };
    }

    fn get_property(&self, _obj: &glib::Object, id: usize) -> Result<glib::Value, ()> {
        let prop = &PROPERTIES[id];
        let settings = &self.settings.lock().unwrap();
        match *prop {
            subclass::Property("location", ..) => {
                let location = settings
                    .location
                    .as_ref()
                    .map(|location| location.to_string());
                Ok(location.to_value())
            }
            subclass::Property("serial", ..) => {
                let serial = settings
                    .serial
                    .as_ref()
                    .map(|location| location.to_string());
                Ok(serial.to_value())
            }
            subclass::Property("framerate", ..) => Ok(settings.framerate.to_value()),
            subclass::Property("depth_width", ..) => Ok(settings.depth.width.to_value()),
            subclass::Property("depth_height", ..) => Ok(settings.depth.height.to_value()),
            subclass::Property("enable_color", ..) => Ok(settings.color.enabled.to_value()),
            subclass::Property("color_width", ..) => Ok(settings.color.resolution.width.to_value()),
            subclass::Property("color_height", ..) => {
                Ok(settings.color.resolution.height.to_value())
            }
            subclass::Property("enable_infra1", ..) => Ok(settings.infra.0.to_value()),
            subclass::Property("enable_infra2", ..) => Ok(settings.infra.1.to_value()),
            _ => unimplemented!(),
        }
    }

    fn constructed(&self, obj: &glib::Object) {
        self.parent_constructed(obj);

        let element = obj.downcast_ref::<gst_base::BaseSrc>().unwrap();
        element.set_format(gst::Format::Bytes);
    }
}

impl ElementImpl for RealsenseSrc {}

impl BaseSrcImpl for RealsenseSrc {
    fn start(&self, element: &gst_base::BaseSrc) -> Result<(), gst::ErrorMessage> {
        let mut state = self.state.lock().unwrap();
        if let State::Started { .. } = *state {
            unreachable!("RealsenseSrc already started");
        }

        let settings = self.settings.lock().unwrap();

        if settings.location == None && settings.serial == None {
            return Err(gst_error_msg!(
                gst::ResourceError::Settings,
                ["Neither the location or the serial properties are defined"]
            ));
        }

        rs2::log::log_to_console(rs2::log::rs2_log_severity::RS2_LOG_SEVERITY_ERROR);
        let config = rs2::config::Config::new().unwrap();

        if let Some(location) = settings.location.as_ref() {
            config
                .enable_device_from_file_repeat_option(location.to_string(), true)
                .unwrap();
        };
        if let Some(serial) = settings.serial.as_ref() {
            if let Some(location) = settings.location.as_ref() {
                config.enable_record_to_file(location.to_string()).unwrap();
            };
            config
                .enable_stream(
                    rs2::pipeline::rs2_stream::RS2_STREAM_DEPTH,
                    settings.depth.width as i32,
                    settings.depth.height as i32,
                    rs2::pipeline::rs2_format::RS2_FORMAT_Z16,
                    settings.framerate as i32,
                )
                .unwrap();

            if settings.color.enabled == true {
                config
                    .enable_stream(
                        rs2::pipeline::rs2_stream::RS2_STREAM_COLOR,
                        settings.color.resolution.width as i32,
                        settings.color.resolution.height as i32,
                        rs2::pipeline::rs2_format::RS2_FORMAT_RGB8,
                        settings.framerate as i32,
                    )
                    .unwrap();
            }

            // TODO: add option to support infra2 stream
            if settings.infra.0 == true {
                config
                    .enable_stream(
                        rs2::pipeline::rs2_stream::RS2_STREAM_INFRARED,
                        settings.depth.width as i32,
                        settings.depth.height as i32,
                        rs2::pipeline::rs2_format::RS2_FORMAT_Y8,
                        settings.framerate as i32,
                    )
                    .unwrap();
            }

            config.enable_device(serial.to_string()).unwrap();
        };

        let context = rs2::context::Context::new().unwrap();
        let pipeline = rs2::pipeline::Pipeline::new(&context).unwrap();
        pipeline.start_with_config(&config).unwrap();

        *state = State::Started { pipeline };

        gst_info!(self.cat, obj: element, "Started");

        Ok(())
    }

    fn stop(&self, element: &gst_base::BaseSrc) -> Result<(), gst::ErrorMessage> {
        let mut state = self.state.lock().unwrap();
        if let State::Stopped = *state {
            return Err(gst_error_msg!(
                gst::ResourceError::Settings,
                ["RealsenseSrc not started"]
            ));
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
            s.fixate_field_nearest_int("width", settings.depth.width as i32);
            s.fixate_field_nearest_int("height", settings.depth.height as i32);
            s.fixate_field_nearest_fraction("framerate", settings.framerate as i32);
        }

        self.parent_fixate(element, caps)
    }

    fn create(
        &self,
        element: &gst_base::BaseSrc,
        _: u64,
        _: u32,
    ) -> Result<gst::Buffer, gst::FlowError> {
        let mut state = self.state.lock().unwrap();

        let pipeline = match *state {
            State::Started { ref mut pipeline } => pipeline,
            State::Stopped => {
                gst_element_error!(element, gst::CoreError::Failed, ["Not started yet"]);
                return Err(gst::FlowError::Error);
            }
        };

        let frames = pipeline.wait_for_frames(10000).unwrap();

        let depth_frame = frames
            .iter()
            .find(|f| {
                f.get_profile().unwrap().get_data().unwrap().stream
                    == rs2::pipeline::rs2_stream::RS2_STREAM_DEPTH
            })
            .unwrap();
        let mut depth_buffer = gst::buffer::Buffer::from_mut_slice(depth_frame.get_data().unwrap());

        let mut depth_tags = gst::tags::TagList::new();
        depth_tags
            .get_mut()
            .unwrap()
            .add::<gst::tags::ExtendedComment>(&"data_type=D", gst::TagMergeMode::Append);
        depth_tags
            .get_mut()
            .unwrap()
            .add::<gst::tags::Title>(&"D", gst::TagMergeMode::Append);
        TagsMeta::add(depth_buffer.get_mut().unwrap(), &mut depth_tags);

        depth_frame.release();

        let settings = self.settings.lock().unwrap();

        if settings.color.enabled == true {
            let color_frame = frames
                .iter()
                .find(|f| {
                    f.get_profile().unwrap().get_data().unwrap().stream
                        == rs2::pipeline::rs2_stream::RS2_STREAM_COLOR
                })
                .unwrap();
            let mut color_buffer =
                gst::buffer::Buffer::from_mut_slice(color_frame.get_data().unwrap());

            let mut color_tags = gst::tags::TagList::new();
            color_tags
                .get_mut()
                .unwrap()
                .add::<gst::tags::ExtendedComment>(&"data_type=RGB", gst::TagMergeMode::Append);
            color_tags
                .get_mut()
                .unwrap()
                .add::<gst::tags::Title>(&"RGB", gst::TagMergeMode::Append);
            TagsMeta::add(color_buffer.get_mut().unwrap(), &mut color_tags);

            BufferMeta::add(depth_buffer.get_mut().unwrap(), &mut color_buffer);

            color_frame.release();
        }

        if settings.infra.0 == true {
            let infra_frame = frames
                .iter()
                .find(|f| {
                    f.get_profile().unwrap().get_data().unwrap().stream
                        == rs2::pipeline::rs2_stream::RS2_STREAM_INFRARED
                })
                .unwrap();
            let mut infra_buffer =
                gst::buffer::Buffer::from_mut_slice(infra_frame.get_data().unwrap());

            let mut infra_tags = gst::tags::TagList::new();
            infra_tags
                .get_mut()
                .unwrap()
                .add::<gst::tags::ExtendedComment>(&"data_type=IR1", gst::TagMergeMode::Append);
            infra_tags
                .get_mut()
                .unwrap()
                .add::<gst::tags::Title>(&"IR1", gst::TagMergeMode::Append);
            TagsMeta::add(infra_buffer.get_mut().unwrap(), &mut infra_tags);

            BufferMeta::add(depth_buffer.get_mut().unwrap(), &mut infra_buffer);

            infra_frame.release();
        }

        Ok(depth_buffer)
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
