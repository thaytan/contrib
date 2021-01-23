#[allow(clippy::module_inception)]
mod rgbdmux;
pub use rgbdmux::register;

mod clock_internals;
mod error;
mod properties;
