mod generated_bindings;
pub use generated_bindings::*;

// For use in `k4a-rs` only, these modules implement Default traits, which are helpful for memory
// allocation. There is no need for these to be public as they are identical to C alternatives.
mod calibration;
mod hardware_version;
mod imu_sample;

// For use in other applications, these modules introduce Rustified structs with Default traits and
// constructors.
mod device_configuration;
pub use device_configuration::*;
mod record_configuration;
pub use record_configuration::*;

// Give direct access to these enumerations in external applications under Rustified name.
pub use k4a_calibration_model_type_t as CalibrationModelType;
pub use k4a_calibration_type_t as CalibrationType;
pub use k4a_color_control_command_t as ColorControlCommand;
pub use k4a_color_resolution_t as ColorResolution;
pub use k4a_depth_mode_t as DepthMode;
pub use k4a_firmware_build_t as FirmwareBuild;
pub use k4a_firmware_signature_t as FirmwareSignature;
pub use k4a_fps_t as Fps;
pub use k4a_hardware_version_t as HardwareVersion;
pub use k4a_image_format_t as ImageFormat;
pub use k4a_playback_seek_origin_t as PlaybackSeekOrigin;
pub use k4a_wired_sync_mode_t as WiredSyncMode;
