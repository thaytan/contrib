use crate::extrinsics::Extrinsics;
use crate::intrinsics::Intrinsics;
use libk4a_sys::k4a_calibration_camera_t;

/// Safe rust wrapper for the [k4a_calibration_camera_t](https://microsoft.github.io/Azure-Kinect-Sensor-SDK/release/1.3.x/structk4a__calibration__camera__t.html) struct.
/// Camera calibration contains intrinsic and extrinsic calibration information for a camera.
pub struct CameraCalibration {
    /// Raw handle to the `k4a::sys` object.
    _raw: k4a_calibration_camera_t,
    /// Resolution width of the calibration sensor.
    pub resolution_width: i32,
    /// Resolution height of the calibration sensor.
    pub resolution_height: i32,
    /// Max FOV of the camera.
    pub metric_radius: f32,
    /// Extrinsic calibration data.
    pub extrinsics: Extrinsics,
    /// Intrinsic calibration data.
    pub intrinsics: Intrinsics,
}

impl CameraCalibration {
    /// Creates a new instance of the [CameraCalibration](struct.CameraCalibration.html) for a raw handle.
    pub(crate) fn new(raw: k4a_calibration_camera_t) -> Self {
        Self {
            _raw: raw,
            resolution_width: raw.resolution_width,
            resolution_height: raw.resolution_height,
            metric_radius: raw.metric_radius,
            extrinsics: Extrinsics::new(raw.extrinsics),
            intrinsics: Intrinsics::new(raw.intrinsics),
        }
    }
}
