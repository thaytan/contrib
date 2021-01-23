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

use glib::{subclass::Property, ParamFlags, ParamSpec};

/// Default value for to `drop-to-synchronise` property
const DEFAULT_DROP_TO_SYNCHRONISE: bool = true;
/// Default value for to `drop-if-missing` property
const DEFAULT_DROP_IF_MISSING: bool = false;
/// Default value for to `deadline-multiplier` property
const DEFAULT_DEADLINE_MULTIPLIER: f32 = 2.50;
/// Default value for to `send-gap-events` property
const DEFAULT_SEND_GAP_EVENTS: bool = false;

pub static PROPERTIES: [Property; 4] = [
    Property("drop-to-synchronise", |name| {
        ParamSpec::boolean(
            name,
            "Drop buffers to synchronise streams",
            "Determines what to do if the timestamps (pts) of the received buffers differ. If set to true, the buffers that are behind, i.e. those that have the smallest pts, get dropped.",
            DEFAULT_DROP_TO_SYNCHRONISE,
            ParamFlags::READWRITE,
        )
    }),
    Property("drop-if-missing", |name| {
        ParamSpec::boolean(
            name,
            "Drop all buffers in one is missing",
            "If enabled, deadline based aggregation is employed with the `deadline-multiplier` property determining the duration of the deadline. If enabled and one of the sink pads does not receive a buffer within the aggregation deadline, all other buffers are dropped.",
            DEFAULT_DROP_IF_MISSING,
            ParamFlags::READWRITE,
        )
    }),
    Property("deadline-multiplier", |name| {
        ParamSpec::float(
            name,
            "Deadline multiplier",
            "Determines the duration of the deadline for the deadline based aggregation. The deadline duration is inversely proportional to the framerate and `deadline-multiplier` is applied as `deadline-multiplier`/`framerate`. Applicable only if `drop-if-missing` is enabled.",
            std::f32::MIN_POSITIVE,
            std::f32::MAX,
            DEFAULT_DEADLINE_MULTIPLIER,
            ParamFlags::READWRITE,
        )
    }),
    Property("send-gap-events", |name| {
        ParamSpec::boolean(
            name,
            "Send gap events downstream",
            "Determines whether to send gap events downstream if buffers are explicitly dropped.",
            DEFAULT_SEND_GAP_EVENTS,
            ParamFlags::READWRITE,
        )
    }),
];

/// A struct containing properties of `rgbdmux` element
pub struct Settings {
    /// Analogous to `drop-if-missing` property
    pub drop_if_missing: bool,
    /// Analogous to `deadline-multiplier` property
    pub deadline_multiplier: f32,
    /// Analogous to `drop-to-synchronise` property
    pub drop_to_synchronise: bool,
    /// Analogous to `send-gap-events` property
    pub send_gap_events: bool,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            drop_if_missing: DEFAULT_DROP_IF_MISSING,
            deadline_multiplier: DEFAULT_DEADLINE_MULTIPLIER,
            drop_to_synchronise: DEFAULT_DROP_TO_SYNCHRONISE,
            send_gap_events: DEFAULT_SEND_GAP_EVENTS,
        }
    }
}
