use crate::error::*;
use libk4a_sys::*;

use crate::image::Image;

/// Struct representation of a [`Capture`](../capture/struct.Capture.html) that wraps around
/// `k4a_capture_t`, which contains a set of images that were captured by a
/// [`Device`](../device/struct.Device.html) at approximately the same time.
pub struct Capture {
    pub(crate) handle: k4a_capture_t,
}

/// Safe releasing of the `k4a_capture_t` handle.
impl Drop for Capture {
    fn drop(&mut self) {
        unsafe {
            k4a_capture_release(self.handle);
        }
    }
}

impl Capture {
    /// Extracts color [`Image`](../image/struct.Image.html) associated with the given
    /// [`Capture`](../capture/struct.Capture.html).
    ///
    /// # Returns
    /// * `Ok(Image)` with color frame on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_color_image(&self) -> Result<Image> {
        let handle = unsafe { k4a_capture_get_color_image(self.handle) };
        if handle.is_null() {
            Err(K4aError::Failure(
                "`Capture` does not contain `color` `Image`",
            ))
        } else {
            Ok(Image { handle })
        }
    }

    /// Extracts depth [`Image`](../image/struct.Image.html) associated with the given
    /// [`Capture`](../capture/struct.Capture.html).
    ///
    /// # Returns
    /// * `Ok(Image)` with depth frame on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_depth_image(&self) -> Result<Image> {
        let handle = unsafe { k4a_capture_get_depth_image(self.handle) };
        if handle.is_null() {
            Err(K4aError::Failure(
                "`Capture` does not contain `depth` `Image`",
            ))
        } else {
            Ok(Image { handle })
        }
    }

    /// Extracts IR [`Image`](../image/struct.Image.html) associated with the given
    /// [`Capture`](../capture/struct.Capture.html).
    ///
    /// # Returns
    /// * `Ok(Image)` with IR frame on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_ir_image(&self) -> Result<Image> {
        let handle = unsafe { k4a_capture_get_ir_image(self.handle) };
        if handle.is_null() {
            Err(K4aError::Failure("`Capture` does not contain `ir` `Image`"))
        } else {
            Ok(Image { handle })
        }
    }

    /// Extracts color [`Image`](../image/struct.Image.html) associated with the given
    /// [`Capture`](../capture/struct.Capture.html).
    ///
    /// # Returns
    /// * Temperature in Celsius (`f32`).
    pub fn get_temperature(&self) -> f32 {
        unsafe { k4a_capture_get_temperature_c(self.handle) }
    }

    /// This function is NOT implemented!
    pub fn new() {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn set_color_image() {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn set_depth_image() {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn set_ir_image() {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn set_temperature() {
        unimplemented!()
    }
}
