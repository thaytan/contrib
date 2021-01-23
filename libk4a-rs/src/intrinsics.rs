use libk4a_sys::{
    k4a_calibration_intrinsic_parameters_t, k4a_calibration_intrinsics_t, CalibrationModelType,
};

/// Struct representation of [k4a_calibration_intrisic_parameters_t](https://microsoft.github.io/Azure-Kinect-Sensor-SDK/release/1.3.x/unionk4a__calibration__intrinsic__parameters__t.html).
#[allow(dead_code)]
#[derive(Debug)]
pub struct IntrinsicsParameters {
    /// Principal point in image, x.
    pub cx: f32,
    /// Principal point in image, y.
    pub cy: f32,
    /// Focal length x.
    pub fx: f32,
    /// Focal length y.
    pub fy: f32,
    /// k1 radial distortion coefficient.
    pub k1: f32,
    /// k2 radial distortion coefficient
    pub k2: f32,
    /// k3 radial distortion coefficient
    pub k3: f32,
    /// k4 radial distortion coefficient
    pub k4: f32,
    /// k5 radial distortion coefficient
    pub k5: f32,
    /// k6 radial distortion coefficient
    pub k6: f32,
    /// Center of distortion in Z=1 plane, x (only used for Rational6KT)
    pub codx: f32,
    /// Center of distortion in Z=1 plane, y (only used for Rational6KT)
    pub cody: f32,
    /// Tangential distortion coefficient 2.
    pub p2: f32,
    /// Tangential distortion coefficient 1.
    pub p1: f32,
    /// Metric radius.
    pub metric_radius: f32,
}

impl IntrinsicsParameters {
    /// Creates a new [IntrinsicsParameters](struct.IntrinsicsParameters.html) from the given raw
    /// handle.
    /// # Arguments
    /// * `params` - A raw instance of the [k4a_calibration_intrisic_parameters_t](https://microsoft.github.io/Azure-Kinect-Sensor-SDK/release/1.3.x/unionk4a__calibration__intrinsic__parameters__t.html), from k4a_sys.
    /// # Returns
    /// - A safe wrapper around the [k4a_calibration_intrisic_parameters_t](https://microsoft.github.io/Azure-Kinect-Sensor-SDK/release/1.3.x/unionk4a__calibration__intrinsic__parameters__t.html).
    pub(crate) fn new(params: k4a_calibration_intrinsic_parameters_t) -> Self {
        // See https://microsoft.github.io/Azure-Kinect-Sensor-SDK/release/1.3.x/unionk4a__calibration__intrinsic__parameters__t.html
        unsafe {
            // TODO: I'm not sure if this is correct. There is a parameter_count on the
            // TODO: k4a_calibration_intrinsics_t, which we might need to use.
            Self {
                cx: params.param.cx,
                cy: params.param.cy,
                fx: params.param.fx,
                fy: params.param.fy,
                k1: params.param.k1,
                k2: params.param.k2,
                k3: params.param.k3,
                k4: params.param.k4,
                k5: params.param.k5,
                k6: params.param.k6,
                codx: params.param.codx,
                cody: params.param.cody,
                p2: params.param.p2,
                p1: params.param.p1,
                metric_radius: params.param.metric_radius,
            }
        }
    }
}

/// Rust wrapper for the [k4a_calibration_intrinsics_t](https://microsoft.github.io/Azure-Kinect-Sensor-SDK/release/1.3.x/structk4a__calibration__intrinsics__t.html).
#[derive(Debug)]
pub struct Intrinsics {
    pub type_: CalibrationModelType,
    pub parameters: IntrinsicsParameters,
}

impl Intrinsics {
    /// Creates a new safe wrapper for the [k4a_calibration_intrinsics_t](https://microsoft.github.io/Azure-Kinect-Sensor-SDK/release/1.3.x/structk4a__calibration__intrinsics__t.html).
    pub(crate) fn new(intrinsics: k4a_calibration_intrinsics_t) -> Self {
        Self {
            type_: intrinsics.type_,
            parameters: IntrinsicsParameters::new(intrinsics.parameters),
        }
    }
}
