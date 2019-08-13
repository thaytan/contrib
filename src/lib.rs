mod generated_bindings;
pub use generated_bindings::*;

// For use in `k4a-rs` only, these modules implement Default traits, which are helpful for memory allocation
mod _calibration;
mod _hardware_version;
mod _imu_sample;

// For use in other applications
mod device_configuration;
pub use device_configuration::*;
mod record_configuration;
pub use record_configuration::*;
