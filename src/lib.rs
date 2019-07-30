#![crate_type = "cdylib"]

#[macro_use]
extern crate glib;
#[macro_use]
extern crate gstreamer as gst;
extern crate gstreamer_base as gst_base;
extern crate gstreamer_depth_meta as meta;
extern crate gstreamer_video as gst_video;
extern crate librealsense2 as rs2;

mod properties_d435;
mod realsensesrc;

fn plugin_init(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    realsensesrc::register(plugin)?;
    Ok(())
}

gst_plugin_define!(
    realsense,
    "Rust HTTP Plugin",
    plugin_init,
    "1.0",
    "MIT/X11",
    "realsense",
    "realsense",
    "https://gitlab.freedesktop.org/gstreamer/gst-plugin-realsense",
    "2019-03-25"
);
