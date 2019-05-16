extern crate glib_sys;
extern crate gstreamer as gst;
extern crate gstreamer_video as gst_video;

use gst::MiniObject;

use crate::sys;
use crate::sys::BufferMeta;

pub trait BufferMetaApi {
    fn add_buffer_meta(&mut self, child_buf: &mut gst::Buffer);
    fn get_buffer_meta(&mut self) -> &BufferMeta;
}

impl BufferMetaApi for gst::buffer::Buffer {
    fn add_buffer_meta(&mut self, child_buf: &mut gst::Buffer) {
        unsafe {
            let meta_buffer = sys::buffer_meta_add(self.as_mut_ptr());
            (*meta_buffer).buffer = child_buf.as_mut_ptr();
        }
    }

    fn get_buffer_meta(&mut self) -> &BufferMeta {
        unsafe {
            &*sys::buffer_meta_get(self.as_mut_ptr())
        }
    }
}
