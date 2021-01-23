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

/// Default value for to `distribute-timestamps` property
const DEFAULT_DISTRIBUTE_TIMESTAMPS: bool = false;

pub static PROPERTIES: [Property; 1] = [Property("distribute-timestamps", |name| {
    ParamSpec::boolean(
            name,
            "Distribute Timestamps",
            "If enabled, timestamps of the main buffers will be distributed to the auxiliary buffers embedded within the `video/rbgd` stream.",
            DEFAULT_DISTRIBUTE_TIMESTAMPS,
            ParamFlags::READWRITE,
        )
})];

/// A struct containing properties of `rgbddemux` element
pub struct Settings {
    /// Analogous to `distribute-timestamps` property
    pub distribute_timestamps: bool,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            distribute_timestamps: DEFAULT_DISTRIBUTE_TIMESTAMPS,
        }
    }
}
