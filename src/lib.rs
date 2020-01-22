// License: Apache 2.0. See LICENSE file in root directory.
// Copyright(c) 2019 Aivero. All Rights Reserved.
#![crate_type = "cdylib"]

extern crate gstreamer as gst;
extern crate gstreamer_sys as gst_sys;

pub use gst::meta::{Meta, MetaAPI, MetaRef, MetaRefMut};

pub mod buffer;
mod sys;
pub mod tags;
