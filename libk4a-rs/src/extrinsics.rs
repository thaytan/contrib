u[derive(Debug)]
pub struct Extrinsics {
    pub rotation: [f32; 9],
    pub translation: [f32; 3],
}

impl Extrinsics {
    pub(crate) fn new(extrinsics: libk4a_sys::k4a_calibration_extrinsics_t) -> Self {
        Self {
            rotation: extrinsics.rotation,
            translation: extrinsics.translation,
        }
    }
}
