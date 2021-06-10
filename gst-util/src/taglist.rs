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

use glib::*;
use gst::*;

pub trait TagListExtension {
    /// Creates a new `TagList` containing a single tag.
    fn new_single<'a, T: Tag<'a>>(value: &T::TagType) -> gst::TagList
    where
        T::TagType: ToSendValue;
}

impl TagListExtension for gst::TagList {
    fn new_single<'a, T: Tag<'a>>(value: &T::TagType) -> gst::TagList
    where
        T::TagType: ToSendValue,
    {
        let mut res = gst::TagList::new();
        res.make_mut().add::<T>(value, gst::TagMergeMode::Append);
        res
    }
}
