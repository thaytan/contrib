#![allow(non_upper_case_globals)]
#![allow(non_camel_case_types)]
#![allow(non_snake_case)]
#![allow(dead_code)]

extern crate glib_sys;
extern crate gstreamer_sys as gst_sys;
extern crate gstreamer_video_sys as gst_video_sys;

#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct BufferMeta {
    pub meta: gst_sys::GstMeta,
    pub buffer: *const gst_sys::GstBuffer,
}
extern "C" {
    pub fn buffer_meta_api_get_type() -> glib_sys::GType;
}
extern "C" {
    pub fn buffer_meta_get_info() -> *const gst_sys::GstMetaInfo;
}
extern "C" {
    pub fn buffer_meta_get(buf: *mut gst_sys::GstBuffer) -> *mut BufferMeta;
}
extern "C" {
    pub fn buffer_meta_add(buf: *mut gst_sys::GstBuffer) -> *mut BufferMeta;
}