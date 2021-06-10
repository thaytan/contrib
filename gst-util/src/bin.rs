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

use crate::element::*;
use crate::error::*;
use crate::orelse;
use glib::*;
use gst::*;

/// Options for the `add_iter` function which extends what the function does.
pub struct Add {
    /// All elements added will also be linked in order `E1 ! E2 ! ... EN`
    pub link: bool,
    /// Will also sync the elements state with the bin they where added to.
    pub sync: bool,
    /// Will take the first and last element and ghost their src/sink pads to the bins src/sink
    /// pad.
    pub ghost: bool,
}

impl Default for Add {
    fn default() -> Self {
        Self {
            link: false,
            sync: false,
            ghost: false,
        }
    }
}

impl Add {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn link() -> Self {
        Self::new().and_link()
    }

    pub fn sync() -> Self {
        Self::new().and_sync()
    }

    pub fn ghost() -> Self {
        Self::new().and_ghost()
    }

    pub fn and_link(mut self) -> Self {
        self.link = true;
        self
    }

    pub fn and_sync(mut self) -> Self {
        self.sync = true;
        self
    }

    pub fn and_ghost(mut self) -> Self {
        self.ghost = true;
        self
    }
}

pub trait BinExtension {
    /// Adds all `elements` to `bin`. Unlike `Bin::add_many`, this function accepts an
    /// `IntoIterator` of elements instead of a slice, which can allow one to avoid creating a
    /// slice when not necessary. This function also takes an `opt` parameter, where one can
    /// turn on more things this function should do while adding elements to the bin.
    /// On failure, this function might leave `bin` with some of, but not all, the elements
    /// added.
    fn add_iter<Elems, ElemRef>(&self, opt: Add, elements: Elems) -> Result<(), ErrorMessage>
    where
        Elems: IntoIterator<Item = ElemRef>,
        ElemRef: AsRef<Element>;
}

impl<T> BinExtension for T
where
    T: IsA<Bin> + IsA<Element>,
{
    fn add_iter<Elems, ElemRef>(&self, opt: Add, elements: Elems) -> Result<(), ErrorMessage>
    where
        Elems: IntoIterator<Item = ElemRef>,
        ElemRef: AsRef<Element>,
    {
        let mut iter = elements.into_iter();
        let mut prev = orelse!(iter.next(), return Ok(()));

        self.add(prev.as_ref())
            .map_err(|e| e.to_err_msg(ResourceError::NoSpaceLeft))?;
        if opt.ghost {
            let pad = prev.as_ref().ghost_static_pad("sink")?;
            self.add_pad(&pad)
                .map_err(|e| e.to_err_msg(CoreError::Pad))?;
        }
        if opt.sync {
            prev.as_ref()
                .sync_state_with_parent()
                .map_err(|e| e.to_err_msg(CoreError::StateChange))?;
        }

        for elem in iter {
            self.add(elem.as_ref())
                .map_err(|e| e.to_err_msg(ResourceError::NoSpaceLeft))?;

            if opt.link {
                prev.as_ref()
                    .link(elem.as_ref())
                    .map_err(|e| e.to_err_msg(CoreError::Pad))?;
            }
            if opt.sync {
                elem.as_ref()
                    .sync_state_with_parent()
                    .map_err(|e| e.to_err_msg(CoreError::StateChange))?;
            }
            prev = elem;
        }

        if opt.ghost {
            let pad = prev.as_ref().ghost_static_pad("src")?;
            self.add_pad(&pad)
                .map_err(|e| e.to_err_msg(CoreError::Pad))?;
        }
        Ok(())
    }
}
