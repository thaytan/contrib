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

use crate::rgbd_timestamps::TimestampMode;

/// A struct that contains data associated with timestamps.
#[derive(Debug, Clone, Copy)]
pub struct TimestampInternals {
    /// Timestamp mode that determines the timestamps of outgoing buffers.
    pub timestamp_mode: TimestampMode,
    /// Contains offset of the first buffer.
    pub stream_start_offset: gst::ClockTime,
    /// Contains common timestamp for a single capture.
    pub frameset_common_timestamp: gst::ClockTime,
    /// Contains duration of each buffer.
    pub buffer_duration: gst::ClockTime,
}

/// Implentation of Default trait for TimestampInternals.
impl Default for TimestampInternals {
    fn default() -> Self {
        Self {
            buffer_duration: gst::CLOCK_TIME_NONE,
            frameset_common_timestamp: gst::CLOCK_TIME_NONE,
            stream_start_offset: gst::CLOCK_TIME_NONE,
            timestamp_mode: TimestampMode::default(),
        }
    }
}
