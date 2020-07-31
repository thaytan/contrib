use k4a_sys::*;

use crate::error::{K4aError, Result};
use std::convert::TryInto;

/// Struct representation of [`Image`](../image/struct.Image.html) that wraps around `k4a_image_t`,
/// which manages an image buffer and associated metadata.
pub struct Image {
    pub(crate) handle: k4a_image_t,
}

/// Safe releasing of the `k4a_image_t` handle.
impl Drop for Image {
    fn drop(&mut self) {
        unsafe {
            k4a_image_release(self.handle);
        }
    }
}

impl Image {
    /// Obtain the size of an [`Image`](../image/struct.Image.html) buffer.
    ///
    /// # Returns
    /// * `Ok(usize)` containing the size in bytes on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_buffer_size(&self) -> Result<usize> {
        let size: u64 = unsafe { k4a_image_get_size(self.handle) };
        if size == 0 {
            Err(K4aError::Failure(
                "`Image` is invalid and has buffer of size 0",
            ))
        } else {
            Ok(size
                .try_into()
                .expect("Could not convert u64 into usize for `Image`"))
        }
    }

    /// Acquire buffer associated with an [`Image`](../image/struct.Image.html).
    ///
    /// # Returns
    /// * `Ok(&[u8])` containing the buffer on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_buffer(&self) -> Result<Vec<u8>> {
        let buffer = unsafe { k4a_image_get_buffer(self.handle) };
        if buffer.is_null() {
            return Err(K4aError::Failure(
                "`Image` is invalid and does not contain a buffer",
            ));
        }
        Ok(unsafe { std::slice::from_raw_parts_mut(buffer, self.get_buffer_size()?).to_vec() })
    }

    /// Obtain the format of an [`Image`](../image/struct.Image.html).
    ///
    /// # Returns
    /// * `ImageFormat` containing the format.
    pub fn get_format(&self) -> ImageFormat {
        unsafe { k4a_image_get_format(self.handle) }
    }

    /// Obtain the width of an [`Image`](../image/struct.Image.html).
    ///
    /// # Returns
    /// * `i32` containing the width in pixels.
    pub fn get_width(&self) -> i32 {
        unsafe { k4a_image_get_width_pixels(self.handle) }
    }

    /// Obtain the height of an [`Image`](../image/struct.Image.html).
    ///
    /// # Returns
    /// * `i32` containing the height in pixels.
    pub fn get_height(&self) -> i32 {
        unsafe { k4a_image_get_height_pixels(self.handle) }
    }

    /// Obtain the stride of an [`Image`](../image/struct.Image.html).
    ///
    /// # Returns
    /// * `i32` containing the stride in bytes.
    pub fn get_stride(&self) -> i32 {
        unsafe { k4a_image_get_stride_bytes(self.handle) }
    }

    /// Obtain the timestamp of an [`Image`](../image/struct.Image.html).
    ///
    /// # Returns
    /// * `u64` containing the timestamp in microseconds.
    pub fn get_timestamp(&self) -> u64 {
        unsafe { k4a_image_get_timestamp_usec(self.handle) }
    }

    /// Obtain the exposure of an [`Image`](../image/struct.Image.html).
    ///
    /// # Returns
    /// * `u64` containing the exposure in microseconds.
    pub fn get_exposure(&self) -> u64 {
        unsafe { k4a_image_get_exposure_usec(self.handle) }
    }

    /// Obtain the white balance of an color [`Image`](../image/struct.Image.html).
    ///
    /// # Returns
    /// * `u32` containing the white balance in Kelvin.
    pub fn get_white_balance(&self) -> u32 {
        unsafe { k4a_image_get_white_balance(self.handle) }
    }

    /// Obtain the ISO speed of an color [`Image`](../image/struct.Image.html).
    ///
    /// # Returns
    /// * `u32` containing the ISO speed.
    pub fn get_iso_speed(&self) -> u32 {
        unsafe { k4a_image_get_iso_speed(self.handle) }
    }

    /// Create new [`Image`](../image/struct.Image.html).
    ///
    /// # Arguments
    /// * `format` - The format of the new [`Image`](../image/struct.Image.html). This function
    /// cannot be used to allocate `K4A_IMAGE_FORMAT_COLOR_MJPG` buffers.
    /// * `width` - Width of the [`Image`](../image/struct.Image.html) in pixels.
    /// * `height` - Height of the [`Image`](../image/struct.Image.html) in pixels.
    /// * `stride` - The number of bytes per horizontal line of the
    /// [`Image`](../image/struct.Image.html).
    ///
    /// # Returns
    /// * `Ok(Image)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn new(format: ImageFormat, width: i32, height: i32, stride: i32) -> Result<Image> {
        let mut image = Image {
            handle: std::ptr::null_mut(),
        };
        match unsafe { k4a_image_create(format, width, height, stride, &mut image.handle) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(image),
            k4a_result_t::K4A_RESULT_FAILED => {
                Err(K4aError::Failure("Failed to create new `Image`"))
            }
        }
    }

    /// This function is NOT implemented!
    pub fn set_timestamp() {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn set_exposure_time() {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn set_white_balance() {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn set_iso_speed() {
        unimplemented!()
    }
}
