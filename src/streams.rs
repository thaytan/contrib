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

use crate::settings::*;

// Unique identifiers of streams
/// ID of the depth stream.
pub(crate) const STREAM_ID_DEPTH: &str = "depth";
/// ID of the IR stream.
pub(crate) const STREAM_ID_IR: &str = "ir";
/// ID of the color stream.
pub(crate) const STREAM_ID_COLOR: &str = "color";
/// ID of the IMU stream.
pub(crate) const STREAM_ID_IMU: &str = "imu";
/// ID of the camera meta stream.
pub(crate) const STREAM_ID_CAMERAMETA: &str = "camerameta";

/// A struct containing information about what streams are enabled.
#[derive(Clone, Copy)]
pub(crate) struct Streams {
    /// Determines whether depth stream is enabled.
    pub(crate) depth: bool,
    /// Determines whether IR stream is enabled.
    pub(crate) ir: bool,
    /// Determines whether color stream is enabled.
    pub(crate) color: bool,
    /// Determines whether IMU stream is enabled.
    pub(crate) imu: bool,
}

pub(crate) struct StreamDescription {
    pub(crate) enabled: bool,
    pub(crate) id: &'static str,
}

impl Default for Streams {
    fn default() -> Self {
        Self {
            depth: DEFAULT_ENABLE_DEPTH,
            ir: DEFAULT_ENABLE_IR,
            color: DEFAULT_ENABLE_COLOR,
            imu: DEFAULT_ENABLE_IMU,
        }
    }
}

impl Streams {
    /// Determine whether at least one video stream is enabled. IMU stream is ignored.
    ///
    /// # Returns
    /// * `true` if at least one video stream is enabled.
    /// * `false` if no stream is enabled.
    pub(crate) fn is_any_video_enabled(self) -> bool {
        self.depth | self.ir | self.color
    }

    /// Determine whether there are any conflict between `enabled_streams` and
    /// `available_streams`
    ///
    /// # Arguments
    /// * `enabled_streams` - The streams that are enabled.
    /// * `available_streams` - The streams that are available.
    ///
    /// # Returns
    /// * `Vec<&str>` of conflicting streams, which is empty if there is no conflict.
    pub(crate) fn are_streams_available(
        enabled_streams: Streams,
        available_streams: Streams,
    ) -> bool {
        (available_streams.imu || !enabled_streams.imu)
            && (available_streams.color || !enabled_streams.color)
            && (available_streams.ir || !enabled_streams.ir)
            && (available_streams.depth || !enabled_streams.depth)
    }

    /// Get a description of all streams sorted by the streams priority
    pub(crate) fn get_descriptions(self) -> [StreamDescription; 4] {
        [
            StreamDescription {
                enabled: self.depth,
                id: STREAM_ID_DEPTH,
            },
            StreamDescription {
                enabled: self.ir,
                id: STREAM_ID_IR,
            },
            StreamDescription {
                enabled: self.color,
                id: STREAM_ID_COLOR,
            },
            StreamDescription {
                enabled: self.imu,
                id: STREAM_ID_IMU,
            },
        ]
    }
}
