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

/// A struct that identifies a stream.
pub struct StreamIdentifier {
    /// The id of the stream.
    pub stream_id: String,
    /// The group id of the stream.
    pub group_id: gst::GroupId,
}

impl StreamIdentifier {
    pub fn build_stream_start_event(&self, stream_name: impl std::fmt::Display) -> gst::Event {
        gst::event::StreamStart::builder(&format!("{}/{}", self.stream_id, stream_name))
            .group_id(self.group_id)
            .build()
    }
}
