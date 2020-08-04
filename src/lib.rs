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

#![crate_type = "cdylib"]

#[macro_use]
extern crate gstreamer as gst;
extern crate gstreamer_base as gst_base;
extern crate gstreamer_sys as gst_sys;

extern crate capnp;
#[allow(clippy::all)]
pub(crate) mod camera_meta_capnp {
    #![allow(dead_code)]
    #![allow(clippy::redundant_field_names)]
    include!(concat!(env!("OUT_DIR"), "/camera_meta_capnp.rs"));
}

mod common;

pub mod camera_meta;
pub mod rgbd;
pub mod rgbd_timestamps;

pub use camera_meta::*;
pub use rgbd::*;
pub use rgbd_timestamps::*;
