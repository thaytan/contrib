pub struct Extrinsics {
    _raw: k4a_sys::k4a_calibration_extrinsics_t,
    pub rotation: [f32; 9],
    pub translation: [f32; 3],
}

impl Extrinsics {
    pub(crate) fn new(extrinsics: k4a_sys::k4a_calibration_extrinsics_t) -> Self {
        Self {
            _raw: extrinsics,
            rotation: extrinsics.rotation,
            translation: extrinsics.translation,
        }
    }
}
