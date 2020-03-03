/// Cross-stream extrinsics: encodes the topology describing how the different cameras are oriented.
#[derive(Debug)]
pub struct Extrinsics {
    /// Column-major 3x3 rotation matrix
    pub rotation: [f32; 9],
    /// Three-element translation vector, in meters
    pub translation: [f32; 3],
}

impl Extrinsics {
    pub(crate) fn new(extrinsics: rs2::rs2_extrinsics) -> Self {
        Self {
            rotation: extrinsics.rotation,
            translation: extrinsics.translation,
        }
    }
}

pub(crate) struct RsExtrinsicsWrapper {
    pub(crate) _handle: rs2::rs2_extrinsics,
}

impl Default for RsExtrinsicsWrapper {
    fn default() -> Self {
        Self {
            _handle: rs2::rs2_extrinsics {
                rotation: [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
                translation: [0.0, 0.0, 0.0],
            },
        }
    }
}
