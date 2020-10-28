// Copyright (C) <2019> Aivero
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Library General Public
// License as published by the Free Software Foundation; either
// version 2 of the License, or (at your option) any later version.
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Library General Public License for more details.
// You should have received a copy of the GNU Library General Public
// License along with this library; if not, write to the
// Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
// Boston, MA 02110-1301, USA.

#![allow(non_upper_case_globals)]
#![allow(non_camel_case_types)]
#![allow(non_snake_case)]
#![allow(dead_code)]

extern crate glib_sys;
extern crate gstreamer_sys as gst_sys;
extern crate gstreamer_video_sys as gst_video_sys;

pub type BufferMeta = _BufferMeta;
pub type TagsMeta = _TagsMeta;

#[repr(C)]
#[derive(Copy, Clone)]
pub struct _BufferMeta {
    pub meta: gst_sys::GstMeta,
    pub buffer: *mut gst_sys::GstBuffer,
}

unsafe impl Sync for _BufferMeta {}
unsafe impl Send for _BufferMeta {}

#[repr(C)]
#[derive(Copy, Clone)]
pub struct _TagsMeta {
    pub meta: gst_sys::GstMeta,
    pub tags: *mut gst_sys::GstTagList,
}

unsafe impl Sync for _TagsMeta {}
unsafe impl Send for _TagsMeta {}

extern "C" {
    pub fn buffer_meta_api_get_type() -> glib_sys::GType;
    pub fn buffer_meta_get_info() -> *const gst_sys::GstMetaInfo;
    pub fn buffer_meta_get(buffer: *mut gst_sys::GstBuffer) -> *mut BufferMeta;
    pub fn buffer_meta_add(
        buffer: *mut gst_sys::GstBuffer,
        buffer_meta: *mut gst_sys::GstBuffer,
    ) -> *mut BufferMeta;
    pub fn tags_meta_api_get_type() -> glib_sys::GType;
    pub fn tags_meta_get_info() -> *const gst_sys::GstMetaInfo;
    pub fn tags_meta_get(buffer: *mut gst_sys::GstBuffer) -> *mut TagsMeta;
    pub fn tags_meta_add(
        buffer: *mut gst_sys::GstBuffer,
        tags_meta: *mut gst_sys::GstTagList,
    ) -> *mut TagsMeta;
}
