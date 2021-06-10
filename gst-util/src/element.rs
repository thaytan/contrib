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

use crate::error::*;
use crate::orelse;
use glib::*;
use gst::*;

pub trait ElementExtension {
    /// Creates a ghost pad with the same name and direction as the pad named `pad_name` in
    /// `element`. This function only ghosts static pads.
    fn ghost_static_pad(&self, pad_name: &str) -> Result<GhostPad, ErrorMessage>;

    /// Links all `elements` together in the same way that `Element::link_many` does. Unlike
    /// `Element::link_many`, this function takes an `IntoIterator` of elements instead of a
    /// slice, which can allow one to avoid creating a slice when not necessary. On failure,
    /// this function might have linked some, but not all, the elements.
    fn link_iter<Elems, ElemRef>(elements: Elems) -> Result<(), ErrorMessage>
    where
        Elems: IntoIterator<Item = ElemRef>,
        ElemRef: AsRef<gst::Element>;
}

impl<T> ElementExtension for T
where
    T: IsA<gst::Element>,
{
    fn ghost_static_pad(&self, pad_name: &str) -> Result<GhostPad, ErrorMessage> {
        let pad = self.get_static_pad(pad_name).ok_or_else(|| {
            gst_error_msg!(CoreError::Pad, ["Element did not have pad '{}'", pad_name])
        })?;

        let direction = pad.get_direction();
        gst::GhostPad::builder(Some(pad_name), direction)
            .build_with_target(&pad)
            .map_err(|e| e.to_err_msg(CoreError::Pad))
    }

    fn link_iter<Elems, ElemRef>(elements: Elems) -> Result<(), ErrorMessage>
    where
        Elems: IntoIterator<Item = ElemRef>,
        ElemRef: AsRef<gst::Element>,
    {
        let mut iter = elements.into_iter();
        let mut prev = orelse!(iter.next(), return Ok(()));
        for elem in iter {
            prev.as_ref()
                .link(elem.as_ref())
                .map_err(|e| e.to_err_msg(CoreError::Pad))?;
            prev = elem;
        }
        Ok(())
    }
}
