#[allow(clippy::module_inception)]
mod rgbddemux;
pub use rgbddemux::register;

mod demux_pad;
mod error;
mod properties;
mod stream_identifier;
