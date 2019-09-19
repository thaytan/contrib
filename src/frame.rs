use std::fmt;

use gst::meta::*;
use gst::BufferRef;
use gst::MiniObject;

use glib;
use glib::translate::from_glib;

use crate::sys;
pub use crate::sys::FrameMeta;

impl FrameMeta {
    pub fn add<'a>(
        buffer: &'a mut BufferRef,
        bytes: &mut Vec<u8>,
    ) -> MetaRefMut<'a, Self, Standalone> {
        unsafe {
            let meta = sys::frame_meta_add(
                buffer.as_mut_ptr(),
                bytes.as_mut_ptr(),
                bytes.len() as std::os::raw::c_ulong,
            );
            Self::from_mut_ptr(buffer, meta)
        }
    }

    pub fn get(buffer: &mut BufferRef) -> &FrameMeta {
        unsafe { &*sys::frame_meta_get(buffer.as_mut_ptr()) }
    }
}

unsafe impl MetaAPI for FrameMeta {
    type GstType = FrameMeta;

    fn get_meta_api() -> glib::Type {
        unsafe { from_glib(sys::frame_meta_api_get_type()) }
    }
}

impl fmt::Debug for FrameMeta {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.debug_struct("FrameMeta")
            .field("bytes", &self.bytes)
            .finish()
    }
}
