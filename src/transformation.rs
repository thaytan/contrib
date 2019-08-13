use crate::calibration::Calibration;
use crate::image::Image;
use crate::utilities::{color_resolution_to_resolution, depth_mode_to_depth_resolution};
use k4a_sys::*;

/// Struct representation of `Transformation` that wraps around `k4a_transformation_t`.
pub struct Transformation {
    pub(crate) handle: k4a_transformation_t,
    calibration_ref: &'static Calibration,
}

// Safe releasing of the `k4a_transformation_t` handle.
impl Drop for Transformation {
    fn drop(&mut self) {
        unsafe {
            k4a_transformation_destroy(self.handle);
        }
    }
}

impl Transformation {
    /// Create new `Transformation`.
    ///
    /// **Parameter:**
    /// * **calibration** - A calibration structure obtained by `Device::get_calibration()`.
    ///
    /// **Return value:**
    /// * **Ok(Transformation)** on success.
    /// * **Err(&str)** on failure.
    pub fn new(calibration: &'static Calibration) -> Result<Transformation, &'static str> {
        let transformation_handle = unsafe { k4a_transformation_create(&calibration.handle) };
        if transformation_handle == std::ptr::null_mut() {
            return Err("`Transformation` could not be created due to invalid `Calibration`");
        }
        Ok(Transformation {
            handle: transformation_handle,
            calibration_ref: calibration,
        })
    }

    /// Transform depth `Image` into the geometry of color camera.
    ///
    /// **Parameter:**
    /// * **depth_image** - Input depth `Image` with format `K4A_IMAGE_FORMAT_DEPTH16`.
    ///
    /// **Return value:**
    /// * **Ok(Image)** contining the new `Image` on success. The resolution of this image is based on color camera resolution and it is with format `K4A_IMAGE_FORMAT_DEPTH16`.
    /// * **Err(&str)** on failure.
    pub fn depth_image_to_color_camera(&self, depth_image: Image) -> Result<Image, &'static str> {
        let color_resolution =
            color_resolution_to_resolution(&(*self.calibration_ref).handle.color_resolution)?;
        let output_image = Image::new(
            k4a_image_format_t::K4A_IMAGE_FORMAT_DEPTH16,
            color_resolution.width,
            color_resolution.height,
            color_resolution.width * 2,
        )?;
        match unsafe {
            k4a_transformation_depth_image_to_color_camera(
                self.handle,
                depth_image.handle,
                output_image.handle,
            )
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(output_image),
            k4a_result_t::K4A_RESULT_FAILED => {
                Err("Failed to transform depth image to color camera geometry")
            }
        }
    }

    /// Transform color `Image` into the geometry of depth camera.
    ///
    /// **Parameter:**
    /// * **depth_image** - Input depth `Image` with format `K4A_IMAGE_FORMAT_DEPTH16`.
    /// * **color_image** - Input color `Image` with format `K4A_IMAGE_FORMAT_COLOR_BGRA32`.
    ///
    /// **Return value:**
    /// * **Ok(Image)** contining the new `Image` on success. The resolution of this image is based on depth camera resolution and it is with format `K4A_IMAGE_FORMAT_COLOR_BGRA32`.
    /// * **Err(&str)** on failure.
    pub fn color_image_to_depth_camera(
        &self,
        depth_image: Image,
        color_image: Image,
    ) -> Result<Image, &'static str> {
        let depth_resolution =
            depth_mode_to_depth_resolution(&(*self.calibration_ref).handle.depth_mode)?;
        let output_image = Image::new(
            k4a_image_format_t::K4A_IMAGE_FORMAT_COLOR_BGRA32,
            depth_resolution.width,
            depth_resolution.height,
            depth_resolution.width * 4,
        )?;
        match unsafe {
            k4a_transformation_color_image_to_depth_camera(
                self.handle,
                depth_image.handle,
                color_image.handle,
                output_image.handle,
            )
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(output_image),
            k4a_result_t::K4A_RESULT_FAILED => {
                Err("Failed to transform color image to depth camera geometry")
            }
        }
    }

    /// Converts depth `Image` into a point cloud.
    ///
    /// **Parameter:**
    /// * **depth_image** - Input depth `Image` with format `K4A_IMAGE_FORMAT_DEPTH16`.
    /// * **perspective** - Geometry in which `depth_image` was computed. If the `depth_image` was captured directly from the depth camera, the value should be `K4A_CALIBRATION_TYPE_DEPTH`. If the `depth_image` is the result of a transformation into the color camera's coordinate space using `Transformation::depth_image_to_color_camera()`, the value should be `K4A_CALIBRATION_TYPE_COLOR`.
    ///
    /// **Return value:**
    /// * **Ok(Image)** contining the new `Image` on success. The resolution of this image is based on depth camera resolution and it is with format `K4A_IMAGE_FORMAT_CUSTOM`, where each pixel contains three 16-bit values (X,Y,Z).
    /// * **Err(&str)** on failure.
    pub fn depth_image_to_point_cloud(
        &self,
        depth_image: Image,
        perspective: k4a_calibration_type_t,
    ) -> Result<Image, &'static str> {
        let depth_resolution =
            depth_mode_to_depth_resolution(&(*self.calibration_ref).handle.depth_mode)?;
        let output_image = Image::new(
            k4a_image_format_t::K4A_IMAGE_FORMAT_CUSTOM,
            depth_resolution.width,
            depth_resolution.height,
            depth_resolution.width * 6,
        )?;
        match unsafe {
            k4a_transformation_depth_image_to_point_cloud(
                self.handle,
                depth_image.handle,
                perspective,
                output_image.handle,
            )
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(output_image),
            k4a_result_t::K4A_RESULT_FAILED => {
                Err("Failed to transform depth image to color camera geometry")
            }
        }
    }
}
