pub mod calibration;
pub mod capture;
pub mod device;
pub mod error;
pub mod image;
pub mod imu_sample;
pub mod playback;
pub mod record;
pub mod transformation;
pub mod utilities;

// Give direct access to these structs in external applications.
pub use k4a_sys::DeviceConfiguration;
pub use k4a_sys::RecordConfiguration;

// Give direct access to these enumerations in external applications.
pub use k4a_sys::CalibrationModelType;
pub use k4a_sys::CalibrationType;
pub use k4a_sys::ColorControlCommand;
pub use k4a_sys::ColorResolution;
pub use k4a_sys::DepthMode;
pub use k4a_sys::FirmwareBuild;
pub use k4a_sys::FirmwareSignature;
pub use k4a_sys::Fps;
pub use k4a_sys::ImageFormat;
pub use k4a_sys::PlaybackSeekOrigin;
pub use k4a_sys::WiredSyncMode;
