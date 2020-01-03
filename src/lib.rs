#[macro_use]
extern crate glib;
#[macro_use]
extern crate gstreamer as gst;
extern crate gstreamer_base as gst_base;
extern crate gstreamer_depth_meta as gst_depth_meta;
#[macro_use]
extern crate lazy_static;

mod rgbddemux;
mod rgbdmux;

fn plugin_init(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    rgbdmux::register(plugin)?;
    rgbddemux::register(plugin)?;
    Ok(())
}

gst_plugin_define!(
    rgbd,
    env!("CARGO_PKG_DESCRIPTION"),
    plugin_init,
    env!("CARGO_PKG_VERSION"),
    "LGPL",
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_REPOSITORY"),
    "2019-09-03"
);
