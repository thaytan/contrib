#![allow(non_upper_case_globals)]
#![allow(non_camel_case_types)]
#![allow(non_snake_case)]
#![allow(dead_code)]

extern crate glib_sys;
extern crate gstreamer_sys as gst_sys;
extern crate gstreamer_video_sys as gst_video_sys;

pub type BufferMeta = _BufferMeta;

#[repr(C)]
#[derive(Copy, Clone)]
pub struct _BufferMeta {
    pub meta: gst_sys::GstMeta,
    pub buffer: *mut gst_sys::GstBuffer,
    pub tags: *mut gst_sys::GstTagList,
}

extern "C" {
    pub fn buffer_meta_api_get_type() -> glib_sys::GType;
    pub fn buffer_meta_get_info() -> *const gst_sys::GstMetaInfo;
    pub fn buffer_meta_get(buffer: *mut gst_sys::GstBuffer) -> *mut BufferMeta;
    pub fn buffer_meta_add(buffer: *mut gst_sys::GstBuffer, buffer_meta: *mut gst_sys::GstBuffer, buffer_tags: *mut gst_sys::GstTagList) -> *mut BufferMeta;
}