use crate::generated_bindings::*;

pub type DeviceConfiguration = k4a_device_configuration_t;

impl DeviceConfiguration {
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        color_format: k4a_image_format_t,
        color_resolution: k4a_color_resolution_t,
        depth_mode: k4a_depth_mode_t,
        camera_fps: k4a_fps_t,
        synchronized_images_only: bool,
        depth_delay_off_color_usec: i32,
        wired_sync_mode: k4a_wired_sync_mode_t,
        subordinate_delay_off_master_usec: u32,
        disable_streaming_indicator: bool,
    ) -> Self {
        DeviceConfiguration {
            color_format,
            color_resolution,
            depth_mode,
            camera_fps,
            synchronized_images_only,
            depth_delay_off_color_usec,
            wired_sync_mode,
            subordinate_delay_off_master_usec,
            disable_streaming_indicator,
        }
    }
}

impl Default for DeviceConfiguration {
    fn default() -> Self {
        DeviceConfiguration {
            color_format: k4a_image_format_t::K4A_IMAGE_FORMAT_COLOR_MJPG,
            color_resolution: k4a_color_resolution_t::K4A_COLOR_RESOLUTION_OFF,
            depth_mode: k4a_depth_mode_t::K4A_DEPTH_MODE_OFF,
            camera_fps: k4a_fps_t::K4A_FRAMES_PER_SECOND_30,
            synchronized_images_only: false,
            depth_delay_off_color_usec: 0,
            wired_sync_mode: k4a_wired_sync_mode_t::K4A_WIRED_SYNC_MODE_STANDALONE,
            subordinate_delay_off_master_usec: 0,
            disable_streaming_indicator: false,
        }
    }
}
