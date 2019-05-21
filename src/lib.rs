#![crate_type = "cdylib"]

extern crate gstreamer as gst;
extern crate gstreamer_sys as gst_sys;

pub use gst::meta::{Meta, MetaAPI, MetaRef, MetaRefMut};

mod sys;
pub mod buffer;
pub mod tags;
