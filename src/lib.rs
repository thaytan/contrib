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
    env!("CARGO_PKG_DESCRIPTION"),
    plugin_init,
    env!("CARGO_PKG_VERSION"),
    "MIT/X11",
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_REPOSITORY"),
    "2019-03-25"
);
