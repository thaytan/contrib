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

#[macro_use]
extern crate glib;
#[macro_use]
extern crate gstreamer as gst;
extern crate gstreamer_base as gst_base;
extern crate gstreamer_depth_meta as gst_depth_meta;
extern crate gstreamer_video as gst_video;
extern crate librealsense2 as rs2;
#[macro_use]
extern crate lazy_static;
extern crate rgbd_timestamps;

mod d400_limits;
mod errors;
mod properties;
mod realsensesrc;
mod rs_meta;
mod settings;
mod streams;

fn plugin_init(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    realsensesrc::register(plugin)?;
    Ok(())
}

gst_plugin_define!(
    gstrealsensesrc,
    env!("CARGO_PKG_DESCRIPTION"),
    plugin_init,
    env!("CARGO_PKG_VERSION"),
    "LGPL",
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_REPOSITORY"),
    env!("BUILD_REL_DATE")
);
