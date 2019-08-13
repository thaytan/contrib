pub mod calibration;
pub mod capture;
pub mod device;
pub mod image;
pub mod imu_sample;
pub mod playback;
pub mod record;
pub mod transformation;
pub mod utilities;

// Give access to these enumerations in external applications
pub use k4a_sys::k4a_calibration_model_type_t as CalibrationModelType;
pub use k4a_sys::k4a_calibration_model_type_t;
pub use k4a_sys::k4a_calibration_type_t as CalibrationType;
pub use k4a_sys::k4a_calibration_type_t;
pub use k4a_sys::k4a_color_control_command_t as ColorControlCommand;
pub use k4a_sys::k4a_color_control_command_t;
pub use k4a_sys::k4a_color_resolution_t as ColorResolution;
pub use k4a_sys::k4a_color_resolution_t;
pub use k4a_sys::k4a_depth_mode_t as DepthMode;
pub use k4a_sys::k4a_depth_mode_t;
pub use k4a_sys::k4a_firmware_build_t as FirmwareBuild;
pub use k4a_sys::k4a_firmware_build_t;
pub use k4a_sys::k4a_firmware_signature_t as FirmwareSignature;
pub use k4a_sys::k4a_firmware_signature_t;
pub use k4a_sys::k4a_fps_t as Fps;
pub use k4a_sys::k4a_fps_t;
pub use k4a_sys::k4a_image_format_t as ImageFormat;
pub use k4a_sys::k4a_image_format_t;
pub use k4a_sys::k4a_playback_seek_origin_t as PlaybackSeekOrigin;
pub use k4a_sys::k4a_playback_seek_origin_t;
pub use k4a_sys::k4a_stream_result_t as StreamResult;
pub use k4a_sys::k4a_stream_result_t;
pub use k4a_sys::k4a_wait_result_t as WaitResult;
pub use k4a_sys::k4a_wait_result_t;
pub use k4a_sys::k4a_wired_sync_mode_t as WiredSyncMode;
pub use k4a_sys::k4a_wired_sync_mode_t;

// Give access to these structures in external applications
pub use k4a_sys::k4a_device_configuration_t;
pub use k4a_sys::k4a_record_configuration_t;
pub use k4a_sys::DeviceConfiguration;
pub use k4a_sys::RecordConfiguration;
