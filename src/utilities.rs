use k4a_sys::*;

use crate::error::{K4aError, Result};

/// Struct representation of `Resolution`.
pub struct Resolution {
    /// Width of image in pixels.
    pub width: i32,
    /// Height of image in pixels.
    pub height: i32,
}

/// Converts `ColorResolution` into `Resolution` for color [`Image`](../image/struct.Image.html).
///
/// # Arguments
/// * `color_resolution` - Color sensor resolution.
///
/// # Returns
/// * `Ok(Resolution)` on success.
/// * `Err(K4aError::Failure)` if given `color_resolution` is `K4A_COLOR_RESOLUTION_OFF`.
pub fn color_resolution_to_resolution(color_resolution: &ColorResolution) -> Result<Resolution> {
    use ColorResolution::*;
    match color_resolution {
        K4A_COLOR_RESOLUTION_OFF => Err(K4aError::Failure("Color stream is disabled")),
        K4A_COLOR_RESOLUTION_720P => Ok(Resolution {
            width: 1280,
            height: 720,
        }),
        K4A_COLOR_RESOLUTION_1080P => Ok(Resolution {
            width: 1920,
            height: 1080,
        }),
        K4A_COLOR_RESOLUTION_1440P => Ok(Resolution {
            width: 2560,
            height: 1440,
        }),
        K4A_COLOR_RESOLUTION_1536P => Ok(Resolution {
            width: 2048,
            height: 1536,
        }),
        K4A_COLOR_RESOLUTION_2160P => Ok(Resolution {
            width: 3840,
            height: 2160,
        }),
        K4A_COLOR_RESOLUTION_3072P => Ok(Resolution {
            width: 4096,
            height: 3072,
        }),
    }
}

/// Converts `DepthMode` into `Resolution` for depth [`Image`](../image/struct.Image.html).
///
/// # Arguments
/// * `depth_mode` - Mode of the depth sensor.
///
/// # Returns
/// * `Ok(Resolution)` on success.
/// * `Err(K4aError::Failure)` if given `depth_mode` is `K4A_DEPTH_MODE_OFF` or
/// `K4A_DEPTH_MODE_PASSIVE_IR`.
pub fn depth_mode_to_depth_resolution(depth_mode: &DepthMode) -> Result<Resolution> {
    use DepthMode::*;
    match depth_mode {
        K4A_DEPTH_MODE_OFF | K4A_DEPTH_MODE_PASSIVE_IR => {
            Err(K4aError::Failure("Depth stream is disabled"))
        }
        K4A_DEPTH_MODE_NFOV_2X2BINNED => Ok(Resolution {
            width: 320,
            height: 288,
        }),
        K4A_DEPTH_MODE_NFOV_UNBINNED => Ok(Resolution {
            width: 640,
            height: 576,
        }),
        K4A_DEPTH_MODE_WFOV_2X2BINNED => Ok(Resolution {
            width: 512,
            height: 512,
        }),
        K4A_DEPTH_MODE_WFOV_UNBINNED => Ok(Resolution {
            width: 1024,
            height: 1024,
        }),
    }
}

/// Converts `DepthMode` into `Resolution` for IR [`Image`](../image/struct.Image.html).
///
/// # Arguments
/// * `depth_mode` - Mode of the depth sensor.
///
/// # Returns
/// * `Ok(Resolution)` on success.
/// * `Err(K4aError::Failure)` if given `depth_mode` is `K4A_DEPTH_MODE_OFF`.
pub fn depth_mode_to_ir_resolution(depth_mode: &DepthMode) -> Result<Resolution> {
    use DepthMode::*;
    match depth_mode {
        K4A_DEPTH_MODE_OFF => Err(K4aError::Failure("IR stream is disabled")),
        K4A_DEPTH_MODE_NFOV_2X2BINNED => Ok(Resolution {
            width: 320,
            height: 288,
        }),
        K4A_DEPTH_MODE_NFOV_UNBINNED => Ok(Resolution {
            width: 640,
            height: 576,
        }),
        K4A_DEPTH_MODE_WFOV_2X2BINNED => Ok(Resolution {
            width: 512,
            height: 512,
        }),
        K4A_DEPTH_MODE_WFOV_UNBINNED | K4A_DEPTH_MODE_PASSIVE_IR => Ok(Resolution {
            width: 1024,
            height: 1024,
        }),
    }
}

/// Converts `Fps` into `i32`.
///
/// # Arguments
/// * `fps` - Frames per second mode of the cameras.
///
/// # Returns
/// * `i32` containing the frames per second.
pub fn fps_to_i32(fps: Fps) -> i32 {
    use Fps::*;
    match fps {
        K4A_FRAMES_PER_SECOND_5 => 5,
        K4A_FRAMES_PER_SECOND_15 => 15,
        K4A_FRAMES_PER_SECOND_30 => 30,
    }
}

/// Determines effective number of bits per pixel based on `image_format`.
///
/// # Arguments
/// * `image_format` - Format of the image.
///
/// # Returns
/// * `Ok(i32)` containing the effective number of bits per pixel on success.
/// * `Err(K4aError::Failure)` if given `image_format` is `K4A_IMAGE_FORMAT_COLOR_MJPG` or
/// `K4A_IMAGE_FORMAT_CUSTOM`.
pub fn image_format_to_bits_per_pixel(image_format: &ImageFormat) -> Result<i32> {
    use ImageFormat::*;
    match image_format {
        K4A_IMAGE_FORMAT_COLOR_MJPG => Err(K4aError::Failure(
            "Compressed MJPG image does not have fixed stride parameter",
        )),
        K4A_IMAGE_FORMAT_CUSTOM => Err(K4aError::Failure(
            "Unknown bit-depth for image with custom format",
        )),
        K4A_IMAGE_FORMAT_CUSTOM8 => Ok(8),
        K4A_IMAGE_FORMAT_COLOR_NV12 => Ok(12),
        K4A_IMAGE_FORMAT_COLOR_YUY2
        | K4A_IMAGE_FORMAT_DEPTH16
        | K4A_IMAGE_FORMAT_IR16
        | K4A_IMAGE_FORMAT_CUSTOM16 => Ok(16),
        K4A_IMAGE_FORMAT_COLOR_BGRA32 => Ok(32),
    }
}
