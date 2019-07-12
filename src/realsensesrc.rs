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

use crate::properties;
use rs2;

static PROPERTIES: [subclass::Property; 12] = [
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
            "Width of the depth frame",
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
            "Height of the depth frame",
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
    subclass::Property("infra_width", |name| {
        glib::ParamSpec::uint(
            name,
            "infra_width",
            "Width of the IR frames",
            properties::INFRA_MIN_WIDTH,
            properties::INFRA_MAX_WIDTH,
            properties::DEFAULT_INFRA_WIDTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("infra_height", |name| {
        glib::ParamSpec::uint(
            name,
            "infra_height",
            "Height of the IR frames",
            properties::INFRA_MIN_HEIGHT,
            properties::INFRA_MAX_HEIGHT,
            properties::DEFAULT_INFRA_HEIGHT,
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
    depth: StreamResolution,
    color: Option<StreamResolution>,
    infra: Option<StereoStream>,
}

impl Default for Settings {
    fn default() -> Self {
        Settings {
            location: None,
            serial: None,
            framerate: properties::DEFAULT_FRAMERATE,
            depth: StreamResolution::new(
                properties::DEFAULT_DEPTH_WIDTH,
                properties::DEFAULT_COLOR_HEIGHT,
            ),
            color: None,
            infra: None,
        }
    }
}

struct StreamResolution {
    width: u32,
    height: u32,
}

impl StreamResolution {
    fn new(width: u32, height: u32) -> Self {
        StreamResolution {
            width: width,
            height: height,
        }
    }
}

struct StereoStream {
    enabled: (bool, bool),
    resolution: StreamResolution,
}

impl StereoStream {
    fn new(enable: (bool, bool), width: u32, height: u32) -> Self {
        StereoStream {
            enabled: enable,
            resolution: StreamResolution::new(width, height),
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
    const NAME: &'static str = "RealsenseSrc";
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
                // ("width", &1280),
                // ("height", &720),
                // ("framerate", &gst::Fraction::new(1, std::i32::MAX)),
                ("width", &gst::IntRange::<i32>::new(1, 1280)),
                ("height", &gst::IntRange::<i32>::new(1, 720)),
                (
                    "framerate",
                    &gst::FractionRange::new(gst::Fraction::new(0, 1), gst::Fraction::new(90, 1)),
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
                let is_enabled = match settings.color {
                    Some(..) => true,
                    None => false,
                };
                if enable_color == is_enabled {
                    return;
                }
                settings.color = match enable_color {
                    true => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `enable_color` to enabled with default resolution"
                        );
                        Some(StreamResolution::new(
                            properties::DEFAULT_COLOR_WIDTH,
                            properties::DEFAULT_COLOR_HEIGHT,
                        ))
                    }
                    false => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `enable_color` to disabled"
                        );
                        None
                    }
                }
            }
            subclass::Property("color_width", ..) => match &mut settings.color {
                None => {
                    gst_warning!(
                        self.cat,
                        obj: element,
                        "Cannot change property `color_width` as `color` stream is not enabled"
                    );
                }
                Some(current_resolution) => {
                    let color_width: u32 = value.get().unwrap();
                    gst_info!(
                        self.cat,
                        obj: element,
                        "Changing property `color_width` from {} to {}",
                        current_resolution.width,
                        color_width
                    );
                    current_resolution.width = color_width;
                }
            },
            subclass::Property("color_height", ..) => match &mut settings.color {
                None => {
                    gst_warning!(
                        self.cat,
                        obj: element,
                        "Cannot change property `color_height` as `color` stream is not enabled"
                    );
                }
                Some(current_resolution) => {
                    let color_height: u32 = value.get().unwrap();
                    gst_info!(
                        self.cat,
                        obj: element,
                        "Changing property `color_height` from {} to {}",
                        current_resolution.width,
                        color_height
                    );
                    current_resolution.width = color_height;
                }
            },
            subclass::Property("enable_infra1", ..) => {
                let enable_infra1 = value.get().unwrap();
                let currently_enabled_units = match &settings.infra {
                    Some(stereo_stream) => stereo_stream.enabled,
                    None => (false, false),
                };
                if enable_infra1 == currently_enabled_units.0 {
                    return;
                }

                match (enable_infra1, currently_enabled_units.1) {
                    (false, false) => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `enable_infra1` to disabled while `enable_infra2` is also disabled"
                        );
                        settings.infra = None;
                    }
                    (false, true) => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `enable_infra1` to disabled while `enable_infra2` is enabled"
                        );
                        if let Some(infra) = &mut settings.infra {
                            infra.enabled.0 = false;
                        }
                    }
                    (true, false) => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `enable_infra1` to enabled with default resolution"
                        );
                        settings.infra = Some(StereoStream::new(
                            (true, false),
                            properties::DEFAULT_INFRA_WIDTH,
                            properties::DEFAULT_INFRA_HEIGHT,
                        ));
                    }
                    (true, true) => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `enable_infra1` to enabled while `enable_infra2` is also enabled"
                        );
                        if let Some(infra) = &mut settings.infra {
                            infra.enabled.0 = true;
                        }
                    }
                }
            }
            subclass::Property("enable_infra2", ..) => {
                let enable_infra2 = value.get().unwrap();
                let currently_enabled_units = match &settings.infra {
                    Some(stereo_stream) => stereo_stream.enabled,
                    None => (false, false),
                };
                if enable_infra2 == currently_enabled_units.1 {
                    return;
                }

                match (currently_enabled_units.0, enable_infra2) {
                    (false, false) => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `enable_infra2` to disabled while `enable_infra1` is also disabled"
                        );
                        settings.infra = None;
                    }
                    (true, false) => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `enable_infra2` to disabled while `enable_infra1` is enabled"
                        );
                        if let Some(infra) = &mut settings.infra {
                            infra.enabled.1 = false;
                        }
                    }
                    (false, true) => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `enable_infra2` to enabled with default resolution"
                        );
                        settings.infra = Some(StereoStream::new(
                            (true, false),
                            properties::DEFAULT_INFRA_WIDTH,
                            properties::DEFAULT_INFRA_HEIGHT,
                        ));
                    }
                    (true, true) => {
                        gst_info!(
                            self.cat,
                            obj: element,
                            "Changing property `enable_infra2` to enabled while `enable_infra1` is also enabled"
                        );
                        if let Some(infra) = &mut settings.infra {
                            infra.enabled.1 = true;
                        }
                    }
                }
            }
            subclass::Property("infra_width", ..) => match &mut settings.infra {
                None => {
                    gst_warning!(
                        self.cat,
                        obj: element,
                        "Cannot change property `infra_width` as neither `infra1` or `infra2` stream is not enabled"
                    );
                }
                Some(current_resolution) => {
                    let infra_width: u32 = value.get().unwrap();
                    gst_info!(
                        self.cat,
                        obj: element,
                        "Changing property `infra_width` from {} to {}",
                        current_resolution.resolution.width,
                        infra_width
                    );
                    current_resolution.resolution.width = infra_width;
                }
            },
            subclass::Property("infra_height", ..) => match &mut settings.infra {
                None => {
                    gst_warning!(
                        self.cat,
                        obj: element,
                        "Cannot change property `infra_height` as neither `infra1` or `infra2` stream is not enabled"
                    );
                }
                Some(current_resolution) => {
                    let infra_height: u32 = value.get().unwrap();
                    gst_info!(
                        self.cat,
                        obj: element,
                        "Changing property `infra_height` from {} to {}",
                        current_resolution.resolution.width,
                        infra_height
                    );
                    current_resolution.resolution.width = infra_height;
                }
            },
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
            subclass::Property("enable_color", ..) => match settings.color {
                Some(..) => Ok(true.to_value()),
                None => Ok(false.to_value()),
            },
            subclass::Property("color_width", ..) => match &settings.color {
                Some(resolution) => Ok(resolution.width.to_value()),
                None => Ok(properties::DEFAULT_COLOR_WIDTH.to_value()),
            },
            subclass::Property("color_height", ..) => match &settings.color {
                Some(resolution) => Ok(resolution.height.to_value()),
                None => Ok(properties::DEFAULT_COLOR_HEIGHT.to_value()),
            },
            subclass::Property("enable_infra1", ..) => match settings.infra {
                Some(..) => Ok(true.to_value()),
                None => Ok(false.to_value()),
            },
            subclass::Property("enable_infra2", ..) => match settings.infra {
                Some(..) => Ok(true.to_value()),
                None => Ok(false.to_value()),
            },
            subclass::Property("infra_width", ..) => match &settings.infra {
                Some(infra) => Ok(infra.resolution.width.to_value()),
                None => Ok(properties::DEFAULT_INFRA_WIDTH.to_value()),
            },
            subclass::Property("infra_height", ..) => match &settings.infra {
                Some(infra) => Ok(infra.resolution.height.to_value()),
                None => Ok(properties::DEFAULT_INFRA_HEIGHT.to_value()),
            },
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

            if let Some(color_resolution) = &settings.color {
                config
                    .enable_stream(
                        rs2::pipeline::rs2_stream::RS2_STREAM_COLOR,
                        color_resolution.width as i32,
                        color_resolution.height as i32,
                        rs2::pipeline::rs2_format::RS2_FORMAT_RGB8,
                        settings.framerate as i32,
                    )
                    .unwrap();
            }

            // TODO: add option to have infra1 || infra2 || (infra1 && infra2)
            if let Some(infra) = &settings.infra {
                config
                    .enable_stream(
                        rs2::pipeline::rs2_stream::RS2_STREAM_INFRARED,
                        infra.resolution.width as i32,
                        infra.resolution.height as i32,
                        // TODO: check whether format is correct
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

        if let Some(..) = settings.color {
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

        if let Some(..) = settings.infra {
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
                .add::<gst::tags::ExtendedComment>(&"data_type=IR", gst::TagMergeMode::Append);
            infra_tags
                .get_mut()
                .unwrap()
                .add::<gst::tags::Title>(&"IR", gst::TagMergeMode::Append);
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
