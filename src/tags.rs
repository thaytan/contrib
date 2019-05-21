use std::fmt;

use gst::BufferRef;
use gst::MiniObject;
use gst::meta::*;

use glib;
use glib::translate::from_glib;

use crate::sys;
pub use crate::sys::TagsMeta;

impl TagsMeta {
    pub fn add<'a>(buffer: &'a mut BufferRef, meta_tags: &mut gst::TagList) -> MetaRefMut<'a, Self, Standalone> {
        unsafe {
            let meta = sys::tags_meta_add(buffer.as_mut_ptr(), meta_tags.as_mut_ptr());
            Self::from_mut_ptr(buffer, meta)
        }
    }

    pub fn get(buffer: &mut BufferRef) -> &TagsMeta {
        unsafe {
            &*sys::tags_meta_get(buffer.as_mut_ptr())
        }
    }
}

unsafe impl MetaAPI for TagsMeta {
    type GstType = TagsMeta;

    fn get_meta_api() -> glib::Type {
        unsafe { from_glib(sys::tags_meta_api_get_type()) }
    }
}

impl fmt::Debug for TagsMeta {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.debug_struct("TagsMeta")
            .field("tags", &self.tags)
            .finish()
    }
}
