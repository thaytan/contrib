use crate::image::Image;
use k4a_sys::*;

/// Struct representation of a `Capture` that wraps around `k4a_capture_t`, which contains a set of images that were captured by a `Device` at approximately the same time.
pub struct Capture {
    pub(crate) handle: k4a_capture_t,
}

// Safe releasing of the `k4a_capture_t` handle.
impl Drop for Capture {
    fn drop(&mut self) {
        unsafe {
            k4a_capture_release(self.handle);
        }
    }
}

impl Capture {
    /// Extracts color `Image` associated with the given `Capture`.
    ///
    /// **Return value:**
    /// * Color **Image**.
    pub fn get_color_image(&self) -> Image {
        Image {
            handle: unsafe { k4a_capture_get_color_image(self.handle) },
        }
    }

    /// Extracts depth `Image` associated with the given `Capture`.
    ///
    /// **Return value:**
    /// * Depth **Image**.
    pub fn get_depth_image(&self) -> Image {
        Image {
            handle: unsafe { k4a_capture_get_depth_image(self.handle) },
        }
    }

    /// Extracts IR `Image` associated with the given `Capture`.
    ///
    /// **Return value:**
    /// * IR **Image**.
    pub fn get_ir_image(&self) -> Image {
        Image {
            handle: unsafe { k4a_capture_get_ir_image(self.handle) },
        }
    }

    /// Extracts color `Image` associated with the given `Capture`.
    ///
    /// **Return value:**
    /// * Temperature in Celsius (**f32**).
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
