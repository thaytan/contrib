// Aivero
// Copyright (C) <2019> Aivero
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Library General Public
// License as published by the Free Software Foundation; either
// version 2 of the License, or (at your option) any later version.
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Library General Public License for more details.
// You should have received a copy of the GNU Library General Public
// License along with this library; if not, write to the
// Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
// Boston, MA 02110-1301, USA.

use super::error::*;

/// Convert `libk4a::ImageFormat` into `&str` that contains appropriate GStreamer CAPS format.
///
/// # Arguments
/// * `image_format` - image format to convert.
///
/// # Returns
/// * `Ok(&'static str)` on sucess.
/// * `Err(K4aError::Failure)` if conversion of custom format is attempted.
pub(crate) fn k4a_image_format_to_gst_video_format(
    image_format: libk4a::ImageFormat,
) -> Result<&'static str, K4aSrcError> {
    use gst_video::VideoFormat;
    use libk4a::ImageFormat::*;
    match image_format {
        K4A_IMAGE_FORMAT_COLOR_MJPG => Ok("image/jpeg"),
        K4A_IMAGE_FORMAT_COLOR_NV12 => Ok(VideoFormat::Nv12.to_str()),
        K4A_IMAGE_FORMAT_COLOR_YUY2 => Ok(VideoFormat::Yuy2.to_str()),
        K4A_IMAGE_FORMAT_COLOR_BGRA32 => Ok(VideoFormat::Bgra.to_str()),
        K4A_IMAGE_FORMAT_DEPTH16 => Ok(VideoFormat::Gray16Le.to_str()),
        K4A_IMAGE_FORMAT_IR16 => Ok(VideoFormat::Gray16Le.to_str()),
        K4A_IMAGE_FORMAT_CUSTOM | K4A_IMAGE_FORMAT_CUSTOM8 | K4A_IMAGE_FORMAT_CUSTOM16 => Err(
            K4aSrcError::Failure("k4asrc: Cannot convert custom k4a format to gst video format"),
        ),
    }
}
