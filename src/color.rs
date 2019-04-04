extern crate glib_sys;
extern crate gstreamer as gst;
extern crate gstreamer_video as gst_video;

use gst::MiniObject;

use crate::sys;
use crate::sys::ColorMeta;

pub fn add_color_meta(parent_buf: &mut gst::buffer::Buffer, child_buf: gst::buffer::Buffer) {
    unsafe {
        let meta_color = sys::color_meta_add(parent_buf.as_mut_ptr());
        (*meta_color).color_buffer = child_buf.as_ptr();
    }
}

pub fn get_color_meta(buffer: &mut gst::buffer::BufferRef) -> &ColorMeta {
    unsafe {
        &*sys::color_meta_get(buffer.as_mut_ptr())
    }
}
