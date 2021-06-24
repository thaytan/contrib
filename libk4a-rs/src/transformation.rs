use libk4a_sys::*;

use crate::calibration::Calibration;
use crate::error::{K4aError, Result};
use crate::image::Image;
use crate::utilities::{
    color_resolution_to_resolution, depth_mode_to_depth_resolution, Resolution,
};

/// Struct representation of [`Transformation`](../transformation/struct.Transformation.html) that
/// wraps around `k4a_transformation_t`.
pub struct Transformation {
    pub(crate) handle: k4a_transformation_t,
    depth_resolution: Resolution,
    color_resolution: Resolution,
}

/// Required for moving between threads
unsafe impl Send for Transformation {}
unsafe impl Sync for Transformation {}

/// Safe releasing of the `k4a_transformation_t` handle.
impl Drop for Transformation {
    fn drop(&mut self) {
        unsafe {
            k4a_transformation_destroy(self.handle);
        }
    }
}

impl Transformation {
    /// Create new [`Transformation`](../transformation/struct.Transformation.html).
    ///
    /// # Arguments
    /// * [`Calibration`](../calibration/struct.Calibration.html) - A calibration structure
    /// obtained by
    /// [`Device::get_calibration()`](../device/struct.Device.html#method.get_calibration).
    ///
    /// # Returns
    /// * `Ok(Transformation)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn new(calibration: &Calibration) -> Result<Transformation> {
        let transformation_handle = unsafe { k4a_transformation_create(&calibration.handle) };
        if transformation_handle.is_null() {
            return Err(K4aError::Failure(
                "`Transformation` could not be created due to invalid `Calibration`",
            ));
        }
        Ok(Transformation {
            handle: transformation_handle,
            depth_resolution: depth_mode_to_depth_resolution(calibration.handle.depth_mode)?,
            color_resolution: color_resolution_to_resolution(calibration.handle.color_resolution)?,
        })
    }

    /// Transform depth [`Image`](../image/struct.Image.html) into the geometry of color camera.
    ///
    /// # Arguments
    /// * `depth_image` - Input depth [`Image`](../image/struct.Image.html) with format
    /// `K4A_IMAGE_FORMAT_DEPTH16`.
    ///
    /// # Returns
    /// * `Ok(Image)` contining the new `Image` on success. The resolution of this image is based
    /// on color camera resolution and it is with format `K4A_IMAGE_FORMAT_DEPTH16`.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn depth_image_to_color_camera(&self, depth_image: Image) -> Result<Image> {
        let output_image = Image::new(
            ImageFormat::K4A_IMAGE_FORMAT_DEPTH16,
            self.color_resolution.width,
            self.color_resolution.height,
            2 * self.color_resolution.width,
        )?;
        match unsafe {
            k4a_transformation_depth_image_to_color_camera(
                self.handle,
                depth_image.handle,
                output_image.handle,
            )
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(output_image),
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to transform depth image to color camera geometry",
            )),
        }
    }

    /// Transform color [`Image`](../image/struct.Image.html) into the geometry of depth camera.
    ///
    /// # Arguments
    /// * `depth_image` - Input depth [`Image`](../image/struct.Image.html) with format
    /// `K4A_IMAGE_FORMAT_DEPTH16`.
    /// * `color_image` - Input color [`Image`](../image/struct.Image.html) with format
    /// `K4A_IMAGE_FORMAT_COLOR_BGRA32`.
    ///
    /// # Returns
    /// * `Ok(Image)` contining the new `Image` on success. The resolution of this image is based
    /// on depth camera resolution and it is with format `K4A_IMAGE_FORMAT_COLOR_BGRA32`.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn color_image_to_depth_camera(
        &self,
        depth_image: Image,
        color_image: Image,
    ) -> Result<Image> {
        let output_image = Image::new(
            ImageFormat::K4A_IMAGE_FORMAT_COLOR_BGRA32,
            self.depth_resolution.width,
            self.depth_resolution.height,
            4 * self.depth_resolution.width,
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
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to transform color image to depth camera geometry",
            )),
        }
    }

    /// Converts depth [`Image`](../image/struct.Image.html) into a point cloud.
    ///
    /// # Arguments
    /// * `depth_image` - Input depth [`Image`](../image/struct.Image.html) with format
    /// `K4A_IMAGE_FORMAT_DEPTH16`.
    /// * `perspective` - Geometry in which `depth_image` was computed. If the `depth_image` was
    /// captured directly from the depth camera, the value should be `K4A_CALIBRATION_TYPE_DEPTH`.
    /// If the `depth_image` is the result of a transformation into the color camera's coordinate
    /// space using `Transformation::depth_image_to_color_camera()`, the value should be
    /// `K4A_CALIBRATION_TYPE_COLOR`.
    ///
    /// # Returns
    /// * `Ok(Image)` contining the new `Image` on success. The resolution of this image is based
    /// on depth camera resolution and it is with format `K4A_IMAGE_FORMAT_CUSTOM`, where each
    /// pixel contains three 16-bit values (X,Y,Z).
    /// * `Err(K4aError::Failure)` on failure.
    pub fn depth_image_to_point_cloud(
        &self,
        depth_image: Image,
        perspective: CalibrationType,
    ) -> Result<Image> {
        let output_image = Image::new(
            ImageFormat::K4A_IMAGE_FORMAT_CUSTOM,
            self.depth_resolution.width,
            self.depth_resolution.height,
            6 * self.depth_resolution.width,
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
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to transform depth image to point cloud",
            )),
        }
    }
}
