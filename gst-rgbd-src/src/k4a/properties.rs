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

use super::enums::{K4aColorFormat, K4aColorResolution, K4aDepthMode, K4aFramerate};
use super::settings::*;
use crate::timestamps::timestamp_mode::TimestampMode;
use glib::subclass;
use glib::StaticType;

lazy_static! {
/// All properties that `k4asrc` element supports.
pub(crate) static ref PROPERTIES: [subclass::Property<'static>; 16] = [
    subclass::Property("serial", |name| {
        glib::ParamSpec::string(
            name,
            "Serial Number",
            "Serial number of a K4A device. If unchanged or empty, `recording-location` is used to \
             locate a file to play from. If both `serial` and `recording-location` are unchanged or \
             empty, first detected device will be used for streaming.",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("recording-location", |name| {
        glib::ParamSpec::string(
            name,
            "Recording File Location",
            "Location of a recording file to play from. If unchanged or empty, physical device \
             specified by `serial` is used. If both `serial` and `recording-location` are unchanged \
             or empty, first detected device will be used.",
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
    subclass::Property("enable-ir", |name| {
        glib::ParamSpec::boolean(
            name,
            "Enable IR",
            "Enables IR stream. If enabled and `enable-depth` is set to false, the IR resolution \
             is set to 1024x1024 px, otherwise the resolution is determined by `depth-mode` \
             property.",
            DEFAULT_ENABLE_IR,
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
    subclass::Property("enable-imu", |name| {
        glib::ParamSpec::boolean(
            name,
            "Enable IMU",
            "Enables IMU stream.",
            DEFAULT_ENABLE_IMU,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color-format", |name| {
        // Note: It is possible to convert the color format also when streaming from Playback
        // by the use of `k4a_playback_set_color_conversion()` (not tested). However, the decision
        // is to use GStreamer conversion for such purposes instead.
        glib::ParamSpec::enum_(
            name,
            "Color Format",
            "Format of the color stream, applicable only when streaming from device",
            K4aColorFormat::static_type(),
            DEFAULT_COLOR_FORMAT as i32,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color-resolution", |name| {
        glib::ParamSpec::enum_(
            name,
            "Color Resolution",
            "Resolution of the color stream, applicable only when streaming from device",
            K4aColorResolution::static_type(),
            DEFAULT_COLOR_RESOLUTION as i32,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("depth-mode", |name| {
        glib::ParamSpec::enum_(
            name,
            "Depth Mode",
            "Depth capture mode configuration, applicable only when streaming from device",
            K4aDepthMode::static_type(),
            DEFAULT_DEPTH_MODE as i32,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("framerate", |name| {
        glib::ParamSpec::enum_(
            name,
            "Framerate",
            "Common framerate of the selected video streams, applicable only when streaming from device.",
            K4aFramerate::static_type(),
            DEFAULT_FRAMERATE as i32,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("get-capture-timeout", |name| {
        glib::ParamSpec::int(
            name,
            "Get Capture Timeout",
            "Timeout used while waiting for capture from a K4A device in milliseconds. Applicable \
             only when streaming from device",
            1,
            std::i32::MAX,
            DEFAULT_GET_CAPTURE_TIMEOUT,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("loop-recording", |name| {
        glib::ParamSpec::boolean(
            name,
            "Loop recording",
            "Enables looping of playing from recording recording specified by `recording-location` \
             property. This property applies only when streaming from Playback. This property cannot \
             be enabled if `timestamp-mode=camera_common` or `timestamp-mode=camera_individual`.",
            DEFAULT_LOOP_RECORDING,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("real-time-playback", |name| {
        glib::ParamSpec::boolean(
            name,
            "Real Time Playback",
            "Determines whether to stream from a recording at the same rate as it was recorded, \
             i.e. pseudo-live source. If set to false, streaming rate will be determined based on \
             the recording rate (and hence the negotiated framerate). If set to false and downstream \
             sink element(s) are set to `async=true`, the streaming rate will be as fast as possible. \
             This property is applicable only when streaming from Playback.",
            DEFAULT_REAL_TIME_PLAYBACK,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("rectify-depth", |name| {
        glib::ParamSpec::boolean(
            name,
            "Rectify Depth",
            "Enables rectification of the depth frames. This produces a depth image where each pixel \
             matches the corresponding pixel coordinate of the color frame, which also means that the \
             resulting depth stream will have resolution equal to the color stream. Note that color \
             stream must be enabled when streaming from a physical device, or recorded as a part of \
             recording that is played back.",
            DEFAULT_RECTIFY_DEPTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("attach-camera-meta", |name| {
        glib::ParamSpec::boolean(
            name,
            "Attach Camera Meta",
            "If enabled, `video/rgbd` will also contain the meta associated with K4A camera, such as \
             intrinsics and extrinsics.",
            DEFAULT_ATTACH_CAMERA_META,
            glib::ParamFlags::READWRITE,
        )
    }),
    // Register "timestamp-mode" property
    TimestampMode::get_property_type(),
];
}
