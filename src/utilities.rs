use k4a_sys::*;

/// Struct representation of an image `Resolution`.
pub struct Resolution {
    pub width: i32,
    pub height: i32,
}

/// Converts `k4a_color_resolution_t` into `Resolution` for color `Image`.
///
/// **Parameter:**
/// * **color_resolution** - Color sensor resolution.
///
/// **Return value:**
/// * **Ok(Resolution)** on success.
/// * **Err(&str)** if given `color_resolution` is `K4A_COLOR_RESOLUTION_OFF`.
pub fn color_resolution_to_resolution(
    color_resolution: &k4a_color_resolution_t,
) -> Result<Resolution, &'static str> {
    match color_resolution {
        k4a_color_resolution_t::K4A_COLOR_RESOLUTION_OFF => Err("Color stream is disabled"),
        k4a_color_resolution_t::K4A_COLOR_RESOLUTION_720P => Ok(Resolution {
            width: 1280,
            height: 720,
        }),
        k4a_color_resolution_t::K4A_COLOR_RESOLUTION_1080P => Ok(Resolution {
            width: 1920,
            height: 1080,
        }),
        k4a_color_resolution_t::K4A_COLOR_RESOLUTION_1440P => Ok(Resolution {
            width: 2560,
            height: 1440,
        }),
        k4a_color_resolution_t::K4A_COLOR_RESOLUTION_1536P => Ok(Resolution {
            width: 2048,
            height: 1536,
        }),
        k4a_color_resolution_t::K4A_COLOR_RESOLUTION_2160P => Ok(Resolution {
            width: 3840,
            height: 2160,
        }),
        k4a_color_resolution_t::K4A_COLOR_RESOLUTION_3072P => Ok(Resolution {
            width: 4096,
            height: 3072,
        }),
    }
}

/// Converts `k4a_depth_mode_t` into `Resolution` for depth `Image`.
///
/// **Parameter:**
/// * **depth_mode** - Mode of the depth sensor.
///
/// **Return value:**
/// * **Ok(Resolution)** on success.
/// * **Err(&str)** if given `depth_mode` is `K4A_DEPTH_MODE_OFF` or `K4A_DEPTH_MODE_PASSIVE_IR`.
pub fn depth_mode_to_depth_resolution(
    depth_mode: &k4a_depth_mode_t,
) -> Result<Resolution, &'static str> {
    match depth_mode {
        k4a_depth_mode_t::K4A_DEPTH_MODE_OFF => Err("Depth stream is disabled"),
        k4a_depth_mode_t::K4A_DEPTH_MODE_NFOV_2X2BINNED => Ok(Resolution {
            width: 320,
            height: 288,
        }),
        k4a_depth_mode_t::K4A_DEPTH_MODE_NFOV_UNBINNED => Ok(Resolution {
            width: 640,
            height: 576,
        }),
        k4a_depth_mode_t::K4A_DEPTH_MODE_WFOV_2X2BINNED => Ok(Resolution {
            width: 512,
            height: 512,
        }),
        k4a_depth_mode_t::K4A_DEPTH_MODE_WFOV_UNBINNED => Ok(Resolution {
            width: 1024,
            height: 1024,
        }),
        k4a_depth_mode_t::K4A_DEPTH_MODE_PASSIVE_IR => Err("Depth stream is disabled"),
    }
}

/// Converts `k4a_depth_mode_t` into `Resolution` for IR `Image`.
///
/// **Parameter:**
/// * **depth_mode** - Mode of the depth sensor.
///
/// **Return value:**
/// * **Ok(Resolution)** on success.
/// * **Err(&str)** if given `depth_mode` is `K4A_DEPTH_MODE_OFF`.
pub fn depth_mode_to_ir_resolution(
    depth_mode: &k4a_depth_mode_t,
) -> Result<Resolution, &'static str> {
    match depth_mode {
        k4a_depth_mode_t::K4A_DEPTH_MODE_OFF => Err("IR stream is disabled"),
        k4a_depth_mode_t::K4A_DEPTH_MODE_NFOV_2X2BINNED => Ok(Resolution {
            width: 320,
            height: 288,
        }),
        k4a_depth_mode_t::K4A_DEPTH_MODE_NFOV_UNBINNED => Ok(Resolution {
            width: 640,
            height: 576,
        }),
        k4a_depth_mode_t::K4A_DEPTH_MODE_WFOV_2X2BINNED => Ok(Resolution {
            width: 512,
            height: 512,
        }),
        k4a_depth_mode_t::K4A_DEPTH_MODE_WFOV_UNBINNED => Ok(Resolution {
            width: 1024,
            height: 1024,
        }),
        k4a_depth_mode_t::K4A_DEPTH_MODE_PASSIVE_IR => Ok(Resolution {
            width: 1024,
            height: 1024,
        }),
    }
}

/// Converts `k4a_fps_t` into `usize`.
///
/// **Parameter:**
/// * **fps** - Frames per second mode of the cameras.
///
/// **Return value:**
/// * **usize** containing the frames per second.
pub fn fps_to_usize(fps: k4a_fps_t) -> usize {
    match fps {
        k4a_fps_t::K4A_FRAMES_PER_SECOND_5 => 5,
        k4a_fps_t::K4A_FRAMES_PER_SECOND_15 => 15,
        k4a_fps_t::K4A_FRAMES_PER_SECOND_30 => 30,
    }
}

/// Determines effective number of bits per pixel based on `image_format`.
///
/// **Parameter:**
/// * **image_format** - Format of the image.
///
/// **Return value:**
/// * **Ok(i32)** containing the effective number of bits per pixel on success.
/// * **Err(&str)** if given `image_format` is `K4A_IMAGE_FORMAT_COLOR_MJPG` or `K4A_IMAGE_FORMAT_CUSTOM`.
pub fn image_format_to_bits_per_pixel(
    image_format: &k4a_image_format_t,
) -> Result<i32, &'static str> {
    match image_format {
        k4a_image_format_t::K4A_IMAGE_FORMAT_COLOR_MJPG => {
            Err("Compressed MJPG image does not have fixed stride parameter")
        }
        k4a_image_format_t::K4A_IMAGE_FORMAT_COLOR_NV12 => Ok(12),
        k4a_image_format_t::K4A_IMAGE_FORMAT_COLOR_YUY2 => Ok(16),
        k4a_image_format_t::K4A_IMAGE_FORMAT_COLOR_BGRA32 => Ok(32),
        k4a_image_format_t::K4A_IMAGE_FORMAT_DEPTH16 => Ok(16),
        k4a_image_format_t::K4A_IMAGE_FORMAT_IR16 => Ok(16),
        k4a_image_format_t::K4A_IMAGE_FORMAT_CUSTOM => {
            Err("Unknown bit-depth for image with custom format")
        }
    }
}
