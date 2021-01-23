pub mod calibration;
pub mod camera_calibration;
pub mod capture;
pub mod device;
pub mod error;
pub mod extrinsics;
pub mod image;
pub mod imu_sample;
pub mod intrinsics;
pub mod playback;
pub mod record;
pub mod transformation;
pub mod utilities;

// Give direct access to these structs in external applications.
pub use libk4a_sys::DeviceConfiguration;
pub use libk4a_sys::RecordConfiguration;

// Give direct access to these enumerations in external applications.
pub use libk4a_sys::CalibrationModelType;
pub use libk4a_sys::CalibrationType;
pub use libk4a_sys::ColorControlCommand;
pub use libk4a_sys::ColorResolution;
pub use libk4a_sys::DepthMode;
pub use libk4a_sys::FirmwareBuild;
pub use libk4a_sys::FirmwareSignature;
pub use libk4a_sys::Fps;
pub use libk4a_sys::ImageFormat;
pub use libk4a_sys::PlaybackSeekOrigin;
pub use libk4a_sys::WiredSyncMode;
