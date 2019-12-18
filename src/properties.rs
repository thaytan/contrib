use glib::{subclass};

use crate::settings::*;
use crate::realsense_timestamp_mode::{realsense_timestamp_mode_get_type};


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
