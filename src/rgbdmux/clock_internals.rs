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

/// Default framerate of the streams
pub const DEFAULT_FRAMERATE: i32 = 30;

/// Internals of the element related to clock that are under Mutex.
pub struct ClockInternals {
    /// Framerate of the streams.
    pub framerate: gst::Fraction,
    /// The duration of one frameset.
    pub frameset_duration: gst::ClockTime,
    /// The duration within which a frameset must arrive if deadline-based aggregation is enabled.
    pub deadline_duration: gst::ClockTime,
    /// The previous timestamps (pts) of the buffers.
    pub previous_timestamp: gst::ClockTime,
    /// A flag that determines whether a GAP event was already sent in consecutive calls. It is used
    /// to create only a single GAP event with unknown duration rather than multiple short GAP events.
    pub is_gap_event_sent: bool,
}

impl Default for ClockInternals {
    fn default() -> Self {
        Self {
            framerate: gst::Fraction::new(DEFAULT_FRAMERATE, 1),
            frameset_duration: gst::CLOCK_TIME_NONE,
            deadline_duration: gst::CLOCK_TIME_NONE,
            previous_timestamp: gst::CLOCK_TIME_NONE,
            is_gap_event_sent: false,
        }
    }
}
