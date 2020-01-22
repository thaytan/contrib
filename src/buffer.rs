// License: Apache 2.0. See LICENSE file in root directory.
// Copyright(c) 2019 Aivero. All Rights Reserved.
use std::fmt;

use gst::meta::*;
use gst::BufferRef;
use gst::MiniObject;

use glib;
use glib::translate::from_glib;

use crate::sys;
pub use crate::sys::BufferMeta;

/// The BufferMeta API is intended to allow developers to add gst buffers as metadata onto buffers.
/// This represents a very generic container format that can hold basically any data.
impl BufferMeta {
    /// Add the given `meta_buffer` onto the given `buffer`, effectively stacking `meta_buffer` onto
    /// `buffer`.
    /// # Arguments
    /// * `buffer` - The base buffer, to which the metadata should be added.
    /// * `meta_buffer` - The buffer that should be added as metadata.
    /// # Example
    /// ```
    /// use gstreamer_depth_meta::buffer::BufferMeta;
    /// gstreamer::init().unwrap();
    /// let mut main_buffer = gstreamer::Buffer::new();
    /// let mut meta_buffer = gstreamer::Buffer::from_slice([10,9,8,7]);
    /// BufferMeta::add(
    ///    main_buffer.make_mut(),
    ///    &mut meta_buffer,
    /// );
    /// ```
    pub fn add<'a>(
        buffer: &'a mut BufferRef,
        meta_buffer: &mut gst::Buffer,
    ) -> MetaRefMut<'a, Self, Standalone> {
        unsafe {
            let meta = sys::buffer_meta_add(buffer.as_mut_ptr(), meta_buffer.as_mut_ptr());
            Self::from_mut_ptr(buffer, meta)
        }
    }

    /// Get a `BufferMeta` on the given buffer.
    /// # Arguments
    /// * `buffer` - The buffer to get a meta buffer from.
    pub fn get(buffer: &BufferRef) -> &BufferMeta {
        unsafe { &*sys::buffer_meta_get(buffer.as_mut_ptr()) }
    }
}

unsafe impl MetaAPI for BufferMeta {
    type GstType = BufferMeta;

    fn get_meta_api() -> glib::Type {
        unsafe { from_glib(sys::buffer_meta_api_get_type()) }
    }
}

impl fmt::Debug for BufferMeta {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.debug_struct("BufferMeta")
            .field("buffer", &self.buffer)
            .finish()
    }
}

mod tests {
    use super::*;

    #[test]
    fn add_and_get_expect_buffers_equal() {
        // Arrange
        gst::init().unwrap();
        let mut buffer = gst::Buffer::new();
        let input = [9, 8, 7, 6];
        let mut meta_buffer = gst::Buffer::from_slice(input);
        let buffer_mut = buffer.make_mut();

        // Act
        BufferMeta::add(buffer_mut, &mut meta_buffer);

        // Assert
        // convert from MetaBuffer into a [u8]
        let meta = BufferMeta::get(buffer_mut);
        let meta_buffer_out = unsafe { gst::buffer::Buffer::from_glib_none(meta.buffer) };
        let meta_buffer_out = meta_buffer_out.map_readable().unwrap();
        let output = meta_buffer_out.as_slice();

        for i in 0..input.len() {
            assert_eq!(input[i], output[i], "Failed for index {}", i);
        }
    }

    #[test]
    fn add_two_and_get_expect_both_buffers_present() {
        // Arrange
        gst::init().unwrap();
        let mut buffer = gst::Buffer::new();
        let input = [9, 8, 7, 6];
        let input_2 = [5, 4, 3, 2];
        let mut meta_buffer = gst::Buffer::from_slice(input);
        let mut meta_buffer_2 = gst::Buffer::from_slice(input_2);
        let buffer_mut = buffer.make_mut();

        // Act
        BufferMeta::add(buffer_mut, &mut meta_buffer);
        BufferMeta::add(buffer_mut, &mut meta_buffer_2);

        let mut number_of_buffers = 0;
        // Assert
        for meta in buffer.iter_meta::<BufferMeta>() {
            let meta_buffer_out = unsafe { gst::buffer::Buffer::from_glib_none(meta.buffer) };
            let meta_buffer_out = meta_buffer_out.map_readable().unwrap();
            let output = meta_buffer_out.as_slice();

            if number_of_buffers == 0 {
                for i in 0..input.len() {
                    assert_eq!(input[i], output[i], "Failed for index {}", i);
                }
            } else {
                for i in 0..input_2.len() {
                    assert_eq!(input_2[i], output[i], "Failed for index {}", i);
                }
            }
            number_of_buffers += 1;
        }
        assert_eq!(number_of_buffers, 2, "Found a wrong number of buffers");
    }

    #[test]
    fn add_and_remove_expect_no_buffers_present() {
        // Arrange
        gst::init().unwrap();
        let mut buffer = gst::Buffer::new();
        let input = [9, 8, 7, 6];
        let mut meta_buffer = gst::Buffer::from_slice(input);
        let buffer_meta = BufferMeta::add(buffer.make_mut(), &mut meta_buffer);

        // Act
        buffer_meta.remove();

        // Assert
        //assert_eq!(s, true);

        for b in buffer.iter_meta::<BufferMeta>() {
            // fail if we get here. There shouldn't be any BufferMetas
            assert_eq!(false, true, "A BufferMeta was found on buffer: {:#?}", b);
        }
    }
}
