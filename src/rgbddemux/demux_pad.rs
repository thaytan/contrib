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

use gst::prelude::*;

/// A handle on the pad, which contains information related to the pad.
pub struct DemuxPad {
    /// The actual pad.
    pub pad: gst::Pad,
    /// A flag to indicate whether or not we have sent the "stream-start" event on the pad.
    pub pushed_stream_start: bool,
}

impl DemuxPad {
    /// Creates a new DemuxPad for the given `pad`.
    /// # Arguments
    /// * `pad` - The pad to create a handle for.
    /// # Returns
    /// A new instance of [DemuxPad](struct.DemuxPad.html) for the pad.
    pub fn new(pad: gst::Pad) -> Self {
        Self {
            pad,
            pushed_stream_start: false,
        }
    }

    /// Deactive and remove `self` (pad) from `element`.
    /// # Arguments
    /// * `element` - The element that represents `rgbddemux` in GStreamer.
    /// # Panics
    /// * If one of the unneeded pads cannot be deactivated or removed from the element.
    pub fn deactivate_and_remove_from_element(&self, element: &gst::Element) {
        // De-activate the pad
        self.pad
            .set_active(false)
            .unwrap_or_else(|_| panic!("Could not deactivate a src pad: {:?}", self.pad));

        // Remove the pad from the element
        element
            .remove_pad(&self.pad)
            .unwrap_or_else(|_| panic!("Could not remove a src pad: {:?}", self.pad));
    }
}
