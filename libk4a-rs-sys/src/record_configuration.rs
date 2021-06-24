use crate::generated_bindings::*;

pub type RecordConfiguration = k4a_record_configuration_t;

impl RecordConfiguration {
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        color_format: k4a_image_format_t,
        color_resolution: k4a_color_resolution_t,
        depth_mode: k4a_depth_mode_t,
        camera_fps: k4a_fps_t,
        color_track_enabled: bool,
        depth_track_enabled: bool,
        ir_track_enabled: bool,
        imu_track_enabled: bool,
        depth_delay_off_color_usec: i32,
        wired_sync_mode: k4a_wired_sync_mode_t,
        subordinate_delay_off_master_usec: u32,
        start_timestamp_offset_usec: u32,
    ) -> Self {
        RecordConfiguration {
            color_format,
            color_resolution,
            depth_mode,
            camera_fps,
            color_track_enabled,
            depth_track_enabled,
            ir_track_enabled,
            imu_track_enabled,
            depth_delay_off_color_usec,
            wired_sync_mode,
            subordinate_delay_off_master_usec,
            start_timestamp_offset_usec,
        }
    }
}

impl Default for RecordConfiguration {
    fn default() -> Self {
        RecordConfiguration {
            color_format: k4a_image_format_t::K4A_IMAGE_FORMAT_COLOR_MJPG,
            color_resolution: k4a_color_resolution_t::K4A_COLOR_RESOLUTION_OFF,
            depth_mode: k4a_depth_mode_t::K4A_DEPTH_MODE_OFF,
            camera_fps: k4a_fps_t::K4A_FRAMES_PER_SECOND_30,
            color_track_enabled: false,
            depth_track_enabled: false,
            ir_track_enabled: false,
            imu_track_enabled: false,
            depth_delay_off_color_usec: 0,
            wired_sync_mode: k4a_wired_sync_mode_t::K4A_WIRED_SYNC_MODE_STANDALONE,
            subordinate_delay_off_master_usec: 0,
            start_timestamp_offset_usec: 0,
        }
    }
}
