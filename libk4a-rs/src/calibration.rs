use libk4a_sys::*;

use crate::camera_calibration::CameraCalibration;
use crate::extrinsics::Extrinsics;

/// Struct representation of [`Calibration`](../calibration/struct.Calibration.html) that wraps
/// around `k4a_calibration_t`.
pub struct Calibration {
    pub(crate) handle: k4a_calibration_t,
}

// The memory the `k4a_calibration_t` is written to is allocated and owned by the caller, so there
// is no need to free or release.

impl Default for Calibration {
    fn default() -> Calibration {
        Calibration {
            handle: k4a_calibration_t::default(),
        }
    }
}

impl Calibration {
    /// Converts raw calibration data into [`Calibration`](../calibration/struct.Calibration.html).
    ///
    /// # Arguments
    /// * `raw_calibration` - Raw calibration data.
    /// * `depth_mode` - Mode of the depth camera.
    /// * `color_resolution` - Resolution of the color camera.
    ///
    /// # Returns
    /// * `Ok(Calibration)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    #[cfg(target_arch = "x86")]
    #[cfg(target_arch = "x86_64")]
    pub fn from_raw(
        raw_calibration: &mut [i8],
        depth_mode: DepthMode,
        color_resolution: ColorResolution,
    ) -> Result<Calibration> {
        let mut calibration_handle = k4a_calibration_t::default();
        match unsafe {
            k4a_calibration_get_from_raw(
                raw_calibration.as_mut_ptr(),
                raw_calibration.len(),
                depth_mode,
                color_resolution,
                &mut calibration_handle,
            )
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(Calibration {
                handle: calibration_handle,
            }),
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to convert raw calibration data into `Calibration`",
            )),
        }
    }

    /// Converts raw calibration data into [`Calibration`](../calibration/struct.Calibration.html).
    ///
    /// # Arguments
    /// * `raw_calibration` - Raw calibration data.
    /// * `depth_mode` - Mode of the depth camera.
    /// * `color_resolution` - Resolution of the color camera.
    ///
    /// # Returns
    /// * `Ok(Calibration)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    #[cfg(target_arch = "arm")]
    #[cfg(target_arch = "aarch64")]
    pub fn from_raw(
        raw_calibration: &mut [u8],
        depth_mode: DepthMode,
        color_resolution: ColorResolution,
    ) -> Result<Calibration> {
        let mut calibration_handle = k4a_calibration_t::default();
        match unsafe {
            k4a_calibration_get_from_raw(
                raw_calibration.as_mut_ptr(),
                raw_calibration.len(),
                depth_mode,
                color_resolution,
                &mut calibration_handle,
            )
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(Calibration {
                handle: calibration_handle,
            }),
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to convert raw calibration data into `Calibration`",
            )),
        }
    }

    /// Get the Depth [CameraCalibration](struct.CameraCalibration.html).
    pub fn depth_camera_calibration(&self) -> CameraCalibration {
        CameraCalibration::new(self.handle.depth_camera_calibration)
    }

    /// Get the Color [CameraCalibration](struct.CameraCalibration.html).
    pub fn color_camera_calibration(&self) -> CameraCalibration {
        CameraCalibration::new(self.handle.color_camera_calibration)
    }

    /// Extrinsic transformation parameters.
    /// The extrinsic parameters allow 3D coordinate conversions between depth camera, color camera,
    /// the IMU's gyroscope and accelerometer. To transform from a source to a target 3D coordinate
    /// system, use the parameters stored under extrinsics(source, target).
    /// # Arguments
    /// * `source` - The source stream, see [k4a::CalibrationType](https://microsoft.github.io/Azure-Kinect-Sensor-SDK/release/1.3.x/group___enumerations_ga8d5fae13125f360be86c166684cdb5c5.html#gga8d5fae13125f360be86c166684cdb5c5a972984dcc30591a8f98034fb582fcfcd).
    /// * `target` - The target stream, see [k4a::CalibrationType](https://microsoft.github.io/Azure-Kinect-Sensor-SDK/release/1.3.x/group___enumerations_ga8d5fae13125f360be86c166684cdb5c5.html#gga8d5fae13125f360be86c166684cdb5c5a972984dcc30591a8f98034fb582fcfcd).
    /// # Returns
    /// The extrinsics from source to target.
    pub fn extrinsics(&self, source: CalibrationType, target: CalibrationType) -> Extrinsics {
        Extrinsics::new(self.handle.extrinsics[source as usize][target as usize])
    }

    /// This function is NOT implemented!
    pub fn convert_2d_to_2d(&self) {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn convert_2d_to_3d(&self) {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn convert_3d_to_2d(&self) {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn convert_3d_to_3d(&self) {
        unimplemented!()
    }
}
