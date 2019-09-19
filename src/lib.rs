#![crate_type = "cdylib"]

extern crate gstreamer as gst;
extern crate gstreamer_sys as gst_sys;

pub use gst::meta::{Meta, MetaAPI, MetaRef, MetaRefMut};

pub mod buffer;
pub mod frame;
mod sys;
pub mod tags;
