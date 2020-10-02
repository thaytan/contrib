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

use std::fmt::{Display, Formatter};

pub(crate) use crate::d400_limits::*;
pub(crate) use crate::enabled_streams::EnabledStreams;
pub(crate) use rs2::stream_profile::StreamResolution;

// Default behaviour of playing from rosbag recording specified by `rosbag-location` property.
pub(crate) const DEFAULT_LOOP_ROSBAG: bool = false;

// Default timeout used while waiting for frames from a realsense device in milliseconds.
pub(crate) const DEFAULT_PIPELINE_WAIT_FOR_FRAMES_TIMEOUT: u32 = 2500;

// Default behaviour for enablind metadata
pub(crate) const DEFAULT_ENABLE_METADATA: bool = false;

// Default behaviour for playing back from rosbag recording.
pub(crate) const DEFAULT_REAL_TIME_ROSBAG_PLAYBACK: bool = false;

/// Default behaviour for attaching camera meta buffers.
pub(crate) const DEFAULT_ATTACH_CAMERA_META: bool = false;

// Streams enabled by defaults
pub(crate) const DEFAULT_ENABLE_DEPTH: bool = true;
pub(crate) const DEFAULT_ENABLE_INFRA1: bool = false;
pub(crate) const DEFAULT_ENABLE_INFRA2: bool = false;
pub(crate) const DEFAULT_ENABLE_COLOR: bool = false;

// Default framerate
pub(crate) const DEFAULT_FRAMERATE: i32 = 30;

// Default resolution of depth, infra1 and infra2 streams
pub(crate) const DEFAULT_DEPTH_WIDTH: i32 = 1280;
pub(crate) const DEFAULT_DEPTH_HEIGHT: i32 = 720;

// Default resolution of color stream
pub(crate) const DEFAULT_COLOR_WIDTH: i32 = 1280;
pub(crate) const DEFAULT_COLOR_HEIGHT: i32 = 720;

/// A struct containing properties of `realsensesrc`
pub(crate) struct Settings {
    pub(crate) serial: Option<String>,
    pub(crate) rosbag_location: Option<String>,
    pub(crate) json_location: Option<String>,
    pub(crate) streams: Streams,
    pub(crate) loop_rosbag: bool,
    pub(crate) wait_for_frames_timeout: u32,
    pub(crate) include_per_frame_metadata: bool,
    pub(crate) real_time_rosbag_playback: bool,
    pub(crate) attach_camera_meta: bool,
}

/// A struct containing properties of `realsensesrc` about streams
#[derive(Debug, Clone, PartialEq)]
pub(crate) struct Streams {
    pub(crate) enabled_streams: EnabledStreams,
    pub(crate) depth_resolution: StreamResolution,
    pub(crate) color_resolution: StreamResolution,
    pub(crate) framerate: i32,
}

impl Display for Streams {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        let depth_info = &format!("{}@{}fps", self.depth_resolution, self.framerate);
        let color_info = &format!("{}@{}fps", self.color_resolution, self.framerate);
        write!(
            f,
            "depth: {}, color: {}, infra1: {}, infra2: {}",
            if self.enabled_streams.depth {
                depth_info
            } else {
                "disabled"
            },
            if self.enabled_streams.color {
                color_info
            } else {
                "disabled"
            },
            if self.enabled_streams.infra1 {
                depth_info
            } else {
                "disabled"
            },
            if self.enabled_streams.infra2 {
                depth_info
            } else {
                "disabled"
            },
        )
    }
}

impl Default for Settings {
    fn default() -> Self {
        Settings {
            rosbag_location: None,
            serial: None,
            json_location: None,
            streams: Streams {
                enabled_streams: EnabledStreams {
                    depth: DEFAULT_ENABLE_DEPTH,
                    infra1: DEFAULT_ENABLE_INFRA1,
                    infra2: DEFAULT_ENABLE_INFRA2,
                    color: DEFAULT_ENABLE_COLOR,
                },
                depth_resolution: StreamResolution {
                    width: DEFAULT_DEPTH_WIDTH,
                    height: DEFAULT_DEPTH_HEIGHT,
                },
                color_resolution: StreamResolution {
                    width: DEFAULT_COLOR_WIDTH,
                    height: DEFAULT_COLOR_HEIGHT,
                },
                framerate: DEFAULT_FRAMERATE,
            },
            loop_rosbag: DEFAULT_LOOP_ROSBAG,
            wait_for_frames_timeout: DEFAULT_PIPELINE_WAIT_FOR_FRAMES_TIMEOUT,
            include_per_frame_metadata: DEFAULT_ENABLE_METADATA,
            real_time_rosbag_playback: DEFAULT_REAL_TIME_ROSBAG_PLAYBACK,
            attach_camera_meta: DEFAULT_ATTACH_CAMERA_META,
        }
    }
}

#[derive(Debug, PartialEq, Clone, Copy)]
pub(crate) enum StreamId {
    Depth,
    Color,
    Infra1,
    Infra2,
}
impl Display for StreamId {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{}",
            match self {
                StreamId::Color => "color",
                StreamId::Depth => "depth",
                StreamId::Infra1 => "infra1",
                StreamId::Infra2 => "infra2",
            }
        )
    }
}
impl StreamId {
    /// Convert RealSense stream type and index into its correspond GStreamer ID.
    ///
    /// # Arguments
    /// * `stream` - Stream type.
    /// * `index` - Index of the sream.
    ///
    /// # Returns
    /// * `&str` containing the ID of the stream.
    pub(crate) fn from_rs2_stream(rs2_stream: rs2::rs2_stream, index: i32) -> Self {
        match rs2_stream {
    rs2::rs2_stream::RS2_STREAM_DEPTH => match index {
        i if i<1 => StreamId::Depth,
        _ => unreachable!("Each RealSense device has only one depth stream, the selected stream index of {} is invalid", index)
    }
    rs2::rs2_stream::RS2_STREAM_INFRARED => match index {
        1 => StreamId::Infra1,
        2 => StreamId::Infra2,
        _ => unreachable!("Each RealSense device has only two infrared streams"),
    },
    rs2::rs2_stream::RS2_STREAM_COLOR =>  match index {
        i if i<1 => StreamId::Color,
        _ => unreachable!("Each RealSense device has only one color stream, the selected stream index of {} is invalid", index)
    }
    _ => unimplemented!("Other RealSense streams are not supported"),
}
    }

    pub(crate) fn to_rs2_stream(self) -> (rs2::rs2_stream, i32) {
        match self {
            StreamId::Depth => (rs2::rs2_stream::RS2_STREAM_DEPTH, -1),
            StreamId::Infra1 => (rs2::rs2_stream::RS2_STREAM_INFRARED, 1),
            StreamId::Infra2 => (rs2::rs2_stream::RS2_STREAM_INFRARED, 2),
            StreamId::Color => (rs2::rs2_stream::RS2_STREAM_COLOR, -1),
        }
    }
}
