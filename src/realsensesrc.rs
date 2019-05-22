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

#[derive(Debug)]
struct Settings {
    location: Option<String>,
    serial: Option<String>,
}

impl Default for Settings {
    fn default() -> Self {
        Settings {
            location: None,
            serial: None,
        }
    }
}

static PROPERTIES: [subclass::Property; 2] = [
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

pub struct RealsenseSrc {
    cat: gst::DebugCategory,
    settings: Mutex<Settings>,
    state: Mutex<State>,
}

impl RealsenseSrc {
    fn set_location(&self, location: Option<String>) -> Result<(), glib::Error> {
        let state = self.state.lock().unwrap();
        if let State::Started { .. } = *state {
            return Err(gst::Error::new(
                gst::URIError::BadState,
                "Changing the `location` property on a started `realsensesrc` is not supported",
            ));
        }

        let mut settings = self.settings.lock().unwrap();
        settings.location = Some(location.unwrap());

        Ok(())
    }

    fn set_serial(&self, serial: Option<String>) -> Result<(), glib::Error> {
        let state = self.state.lock().unwrap();
        if let State::Started { .. } = *state {
            return Err(gst::Error::new(
                gst::URIError::BadState,
                "Changing the `serial` property on a started `realsensesrc` is not supported",
            ));
        }

        let mut settings = self.settings.lock().unwrap();
        settings.serial = Some(serial.unwrap());

        Ok(())
    }
}

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
                "Realsense Source",
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
                //("format", &"RGB"),
                ("format", &"GRAY16_LE"),
                ("width", &1280),
                ("height", &720),
                ("framerate", &gst::Fraction::new(1, std::i32::MAX)),
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
        let prop = &PROPERTIES[id];
        match *prop {
            subclass::Property("location", ..) => {
                let element = obj.downcast_ref::<gst_base::BaseSrc>().unwrap();

                let res = match value.get::<String>() {
                    Some(location) => self.set_location(Some(location)),
                    None => self.set_location(None),
                };

                if let Err(err) = res {
                    gst_error!(
                        self.cat,
                        obj: element,
                        "Failed to set property `location`: {}",
                        err
                    );
                }
            }
            subclass::Property("serial", ..) => {
                let element = obj.downcast_ref::<gst_base::BaseSrc>().unwrap();

                let res = match value.get::<String>() {
                    Some(serial) => self.set_serial(Some(serial)),
                    None => self.set_serial(None),
                };

                if let Err(err) = res {
                    gst_error!(
                        self.cat,
                        obj: element,
                        "Failed to set property `serial`: {}",
                        err
                    );
                }
            }
            _ => unimplemented!(),
        };
    }

    fn get_property(&self, _obj: &glib::Object, id: usize) -> Result<glib::Value, ()> {
        let prop = &PROPERTIES[id];
        match *prop {
            subclass::Property("location", ..) => {
                let settings = self.settings.lock().unwrap();
                let location = settings
                    .location
                    .as_ref()
                    .map(|location| location.to_string());

                Ok(location.to_value())
            }
            subclass::Property("serial", ..) => {
                let settings = self.settings.lock().unwrap();
                let serial = settings
                    .serial
                    .as_ref()
                    .map(|location| location.to_string());

                Ok(serial.to_value())
            }
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
                    1280,
                    720,
                    rs2::pipeline::rs2_format::RS2_FORMAT_Z16,
                    30,
                )
                .unwrap();
            config
                .enable_stream(
                    rs2::pipeline::rs2_stream::RS2_STREAM_COLOR,
                    1280,
                    720,
                    rs2::pipeline::rs2_format::RS2_FORMAT_RGB8,
                    30,
                )
                .unwrap();
            config.enable_device(serial.to_string()).unwrap();
        };

        if settings.location == None && settings.serial == None {
            return Err(gst_error_msg!(
                gst::ResourceError::Settings,
                ["Neither the location or the serial properties are defined"]
            ));
        }

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
        let color_frame = frames
            .iter()
            .find(|f| {
                f.get_profile().unwrap().get_data().unwrap().stream
                    == rs2::pipeline::rs2_stream::RS2_STREAM_COLOR
            })
            .unwrap();

        let mut depth_buffer = gst::buffer::Buffer::from_mut_slice(depth_frame.get_data().unwrap());
        let mut color_buffer = gst::buffer::Buffer::from_mut_slice(color_frame.get_data().unwrap());
        let mut depth_tags = gst::tags::TagList::new();
        depth_tags
            .get_mut()
            .unwrap()
            .add::<gst::tags::ExtendedComment>(&"data_type=D", gst::TagMergeMode::Append);
        depth_tags
            .get_mut()
            .unwrap()
            .add::<gst::tags::Title>(&"D", gst::TagMergeMode::Append);

        let mut color_tags = gst::tags::TagList::new();
        color_tags
            .get_mut()
            .unwrap()
            .add::<gst::tags::ExtendedComment>(&"data_type=RGB", gst::TagMergeMode::Append);

        color_tags
            .get_mut()
            .unwrap()
            .add::<gst::tags::Title>(&"RGB", gst::TagMergeMode::Append);

        TagsMeta::add(depth_buffer.get_mut().unwrap(), &mut depth_tags);

        TagsMeta::add(color_buffer.get_mut().unwrap(), &mut color_tags);
        BufferMeta::add(depth_buffer.get_mut().unwrap(), &mut color_buffer);

        color_frame.release();
        depth_frame.release();

        Ok(depth_buffer)
    }
}

pub fn register(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    gst::Element::register(plugin, "realsensesrc", 256 + 100, RealsenseSrc::get_type())
}
