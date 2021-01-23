/// Rust wrapper for the [`rs2_intrinsics`](https://intelrealsense.github.io/librealsense/doxygen/structrs2__intrinsics.html#details) video stream intrinsics.
#[derive(Debug)]
pub struct Intrinsics {
    /// Width of the image in pixels
    pub width: i32,
    /// Height of the image in pixels
    pub height: i32,
    /// Horizontal coordinate of the principal point of the image, as a pixel offset from the left edge
    pub ppx: f32,
    /// Vertical coordinate of the principal point of the image, as a pixel offset from the top edge
    pub ppy: f32,
    /// Focal length of the image plane, as a multiple of pixel width
    pub fx: f32,
    /// Focal length of the image plane, as a multiple of pixel height
    pub fy: f32,
    /// Distortion model of the image
    pub model: Distortion,
    /// Distortion coefficients
    pub coeffs: [f32; 5],
}

impl Intrinsics {
    pub(crate) fn new(intrinsics: rs2::rs2_intrinsics) -> Self {
        Self {
            width: intrinsics.width,
            height: intrinsics.height,
            ppx: intrinsics.ppx,
            ppy: intrinsics.ppy,
            fx: intrinsics.fx,
            fy: intrinsics.fy,
            model: intrinsics.model,
            coeffs: intrinsics.coeffs,
        }
    }
}

/// Rustified name for `rs2_distortion` struct
pub type Distortion = rs2::rs2_distortion;

pub(crate) struct RsIntrinsicsWrapper {
    pub(crate) _handle: rs2::rs2_intrinsics,
}

impl Default for RsIntrinsicsWrapper {
    fn default() -> Self {
        Self {
            _handle: rs2::rs2_intrinsics {
                width: 0,
                height: 0,
                ppx: 0.0,
                ppy: 0.0,
                fx: 0.0,
                fy: 0.0,
                model: Distortion::RS2_DISTORTION_NONE,
                coeffs: [0.0, 0.0, 0.0, 0.0, 0.0],
            },
        }
    }
}
