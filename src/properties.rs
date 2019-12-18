use glib::{subclass, StaticType, Type};

use crate::settings::*;
use glib::gobject_sys;

#[derive(Debug, Eq, PartialEq, Ord, PartialOrd, Hash, Clone, Copy)]
#[repr(u32)]
pub enum RealsenseTimestampMode {
    Default = 0,
    AllBuffers = 1,
    RS2 = 2,
}
impl glib::translate::ToGlib for RealsenseTimestampMode {
    type GlibType = i32;

    fn to_glib(&self) -> Self::GlibType {
        *self as i32
    }
}
impl glib::translate::FromGlib<i32> for RealsenseTimestampMode {
    fn from_glib(val: i32) -> Self {
        match val {
            0 => RealsenseTimestampMode::Default,
            1 => RealsenseTimestampMode::AllBuffers,
            2 => RealsenseTimestampMode::RS2,
            _ => unreachable!()
        }
    }
}
impl StaticType for RealsenseTimestampMode {
    fn static_type() -> Type {
        realsense_timestamp_mode_get_type()
    }
}
impl<'a> glib::value::FromValueOptional<'a> for RealsenseTimestampMode {
    unsafe fn from_value_optional(value: &glib::Value) -> Option<Self> {
        Some(glib::value::FromValue::from_value(value))
    }
}
impl<'a> glib::value::FromValue<'a> for RealsenseTimestampMode {
    unsafe fn from_value(value: &glib::Value) -> Self {
        use glib::translate::ToGlibPtr;

        glib::translate::from_glib(gobject_sys::g_value_get_enum(value.to_glib_none().0))
    }
}

impl glib::value::SetValue for RealsenseTimestampMode {
    unsafe fn set_value(value: &mut glib::Value, this: &Self) {
        use glib::translate::{ToGlib, ToGlibPtrMut};

        gobject_sys::g_value_set_enum(value.to_glib_none_mut().0, this.to_glib())
    }
}

fn realsense_timestamp_mode_get_type() -> glib::Type {
    use std::sync::Once;
    static ONCE: Once = Once::new();
    static mut TYPE: glib::Type = glib::Type::Invalid;

    ONCE.call_once(|| {
        use std::ffi;
        use std::ptr;

        static mut VALUES: [gobject_sys::GEnumValue; 4] = [
            gobject_sys::GEnumValue {
                value: RealsenseTimestampMode::Default as i32,
                value_name: b"Default: Adds the realsensesrc's Clock Timestamp to only the main (depth) buffer.\0" as *const _ as *const _,
                value_nick: b"default\0" as *const _ as *const _,
            },
            gobject_sys::GEnumValue {
                value: RealsenseTimestampMode::AllBuffers as i32,
                value_name: b"All Buffers: Adds the realsensesrc's Clock Timestamp to all buffers based on the duration since the element was created.\0" as *const _ as *const _,
                value_nick: b"all-buffers\0" as *const _ as *const _,
            },
            gobject_sys::GEnumValue {
                value: RealsenseTimestampMode::RS2 as i32,
                value_name: b"RS2: Stamps librealsense2's timestamps on all buffers.\0" as *const _ as *const _,
                value_nick: b"rs2\0" as *const _ as *const _,
            },
            gobject_sys::GEnumValue {
                value: 0,
                value_name: ptr::null(),
                value_nick: ptr::null(),
            },
        ];

        let name = ffi::CString::new("GstRealsenseTimestampMode").unwrap();
        unsafe {
            let type_ = gobject_sys::g_enum_register_static(name.as_ptr(), VALUES.as_ptr());
            TYPE = glib::translate::from_glib(type_);
        }
    });

    unsafe {
        assert_ne!(TYPE, glib::Type::Invalid);
        TYPE
    }
}


pub(crate) static PROPERTIES: [subclass::Property; 17] = [
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
            DEFAULT_ENABLE_DEPTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable-infra1", |name| {
        glib::ParamSpec::boolean(
            name,
            "Enable Infra1",
            "Enables infra1 stream.",
            DEFAULT_ENABLE_INFRA1,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable-infra2", |name| {
        glib::ParamSpec::boolean(
            name,
            "Enable Infra2",
            "Enables infra2 stream.",
            DEFAULT_ENABLE_INFRA2,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable-color", |name| {
        glib::ParamSpec::boolean(
            name,
            "Enable Color",
            "Enables color stream.",
            DEFAULT_ENABLE_COLOR,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("depth-width", |name| {
        glib::ParamSpec::int(
            name,
            "Depth Width",
            "Width of the depth and infra1/infra2 frames.",
            DEPTH_MIN_WIDTH,
            DEPTH_MAX_WIDTH,
            DEFAULT_DEPTH_WIDTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("depth-height", |name| {
        glib::ParamSpec::int(
            name,
            "Depth Height",
            "Height of the depth and infra1/infra2 frames.",
            DEPTH_MIN_HEIGHT,
            DEPTH_MAX_HEIGHT,
            DEFAULT_DEPTH_HEIGHT,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color-width", |name| {
        glib::ParamSpec::int(
            name,
            "Color Width",
            "Width of the color frame.",
            COLOR_MIN_WIDTH,
            COLOR_MAX_WIDTH,
            DEFAULT_COLOR_WIDTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color-height", |name| {
        glib::ParamSpec::int(
            name,
            "Color Height",
            "Height of the color frame.",
            COLOR_MIN_HEIGHT,
            COLOR_MAX_HEIGHT,
            DEFAULT_COLOR_HEIGHT,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("framerate", |name| {
        glib::ParamSpec::int(
            name,
            "Framerate",
            "Common framerate of the selected streams.",
            MIN_FRAMERATE,
            MAX_FRAMERATE,
            DEFAULT_FRAMERATE,
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
            DEFAULT_ENABLE_METADATA,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("timestamp-mode", |name| {
        glib::ParamSpec::enum_(
            name,
            "The timestamping mode to use on the realsensesrc",
            "Defines the timestamping mode to use on the realsensesrc's buffers and metabuffers.",
            realsense_timestamp_mode_get_type(),
            DEFAULT_TIMESTAMP_MODE as i32,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("real-time-rosbag-playback", |name| {
        glib::ParamSpec::boolean(
            name,
            "Real Time Rosbag Playback",
            "Determines whether to stream from the file the same way it was recorded. If set to false, streaming rate will be determined based on the negotiated framerate or it will be as fast as possible if downstream elements are async.",
            DEFAULT_REAL_TIME_ROSBAG_PLAYBACK,
            glib::ParamFlags::READWRITE,
        )
    }),
];
