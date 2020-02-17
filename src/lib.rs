#[macro_use]
extern crate glib;
#[macro_use]
extern crate gstreamer as gst;
extern crate gstreamer_base as gst_base;
extern crate gstreamer_depth_meta as gst_depth_meta;
extern crate gstreamer_video as gst_video;
#[macro_use]
extern crate lazy_static;
extern crate k4a;

mod enums;
mod error;
mod k4asrc;
mod properties;
mod settings;
mod stream_properties;
mod streams;
mod timestamps;
mod utilities;

fn plugin_init(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    k4asrc::register(plugin)?;
    Ok(())
}

gst_plugin_define!(
    gstk4asrc,
    env!("CARGO_PKG_DESCRIPTION"),
    plugin_init,
    env!("CARGO_PKG_VERSION"),
    "LGPL",
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_REPOSITORY"),
    "2019-12-04" // This date is replaced with Python's datetime.now() during a conan create run.
);
