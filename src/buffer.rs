use std::fmt;

use gst::BufferRef;
use gst::MiniObject;

use glib;
use glib::translate::{from_glib};
use gst::meta::*;

use crate::sys;

impl sys::BufferMeta {
    pub fn add_buffer_meta<'a>(buffer: &'a mut BufferRef, meta_buffer: &mut gst::Buffer, meta_tags: &mut gst::TagList) -> MetaRefMut<'a, Self, Standalone> {
        unsafe {
            let meta = sys::buffer_meta_add(buffer.as_mut_ptr(), meta_buffer.as_mut_ptr(), meta_tags.as_mut_ptr());
            Self::from_mut_ptr(buffer, meta)
        }
    }

    pub fn get_buffer_meta(buffer: &mut BufferRef) -> &sys::BufferMeta {
        unsafe {
            &*sys::buffer_meta_get(buffer.as_mut_ptr())
        }
    }
}

unsafe impl MetaAPI for sys::BufferMeta {
    type GstType = sys::BufferMeta;

    fn get_meta_api() -> glib::Type {
        unsafe { from_glib(sys::buffer_meta_api_get_type()) }
    }
}

impl fmt::Debug for sys::BufferMeta {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.debug_struct("BufferMeta")
            .field("buffer", &self.buffer)
            .finish()
    }
}

