#![allow(non_camel_case_types)]

use crate::generated_bindings::*;

pub type k4a_calibration = k4a_calibration_t;
impl Default for k4a_calibration {
    fn default() -> Self {
        k4a_calibration {
            depth_camera_calibration: k4a_calibration_camera::default(),
            color_camera_calibration: k4a_calibration_camera::default(),
            extrinsics: [[k4a_calibration_extrinsics::default(); 4]; 4],
            depth_mode: k4a_depth_mode_t::K4A_DEPTH_MODE_OFF,
            color_resolution: k4a_color_resolution_t::K4A_COLOR_RESOLUTION_OFF,
        }
    }
}

type k4a_calibration_camera = k4a_calibration_camera_t;
impl Default for k4a_calibration_camera {
    fn default() -> Self {
        k4a_calibration_camera {
            extrinsics: k4a_calibration_extrinsics::default(),
            intrinsics: k4a_calibration_intrinsics::default(),
            resolution_width: 0,
            resolution_height: 0,
            metric_radius: 0.0,
        }
    }
}

type k4a_calibration_extrinsics = k4a_calibration_extrinsics_t;
impl Default for k4a_calibration_extrinsics {
    fn default() -> Self {
        k4a_calibration_extrinsics {
            rotation: [0.0; 9],
            translation: [0.0; 3],
        }
    }
}

type k4a_calibration_intrinsics = k4a_calibration_intrinsics_t;
impl Default for k4a_calibration_intrinsics {
    fn default() -> Self {
        k4a_calibration_intrinsics {
            type_: k4a_calibration_model_type_t::K4A_CALIBRATION_LENS_DISTORTION_MODEL_UNKNOWN,
            parameter_count: 0,
            parameters: k4a_calibration_intrinsic_parameters_t { v: [0.0; 15] },
        }
    }
}
