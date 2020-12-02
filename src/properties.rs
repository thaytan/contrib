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

use glib::subclass;
use rgbd_timestamps::timestamp_mode::TimestampMode;

use crate::settings::*;

lazy_static! {
pub(crate) static ref PROPERTIES: [subclass::Property<'static>; 20] = [
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
            "Enables looping of playing from rosbag recording specified by `rosbag-location` property. This property applies only if `rosbag-location` and no `serial` are specified. This property cannot be enabled if `timestamp-mode=camera_common` or `timestamp-mode=camera_individual`.",
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
            "Attempts to include librealsense2's per-frame metadata as an additional buffer on the main buffer. Per-frame metadata is silently ignored if it cannot be fetched from the librealsense2 frames.",
            DEFAULT_ENABLE_METADATA,
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
    subclass::Property("attach-camera-meta", |name| {
        glib::ParamSpec::boolean(
            name,
            "Attach Camera Meta",
            "If enabled, `video/rgbd` will also contain the meta associated with RealSense camera, such as \
             intrinsics and extrinsics.",
            DEFAULT_ATTACH_CAMERA_META,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("align-from", |name| {
        glib::ParamSpec::string(
            name,
            "Comma-separated list of string to to align",
            "If not empty, the realsensesrc will align the specified frames to the frame specified in align-to (target).",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("align-to", |name| {
        glib::ParamSpec::string(
            name,
            "The stream to align to",
            "The name of the stream to align to (target).",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    // Register "timestamp-mode" property
    TimestampMode::get_property_type()
];
}
