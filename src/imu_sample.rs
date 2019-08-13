use k4a_sys::*;

/// Struct representation of `ImuSample` that wraps around `k4a_imu_sample_t`, which manages an IMU buffer and associated metadata.
pub struct ImuSample {
    pub(crate) handle: k4a_imu_sample_t,
}

// The memory the `k4a_imu_sample` is written to is allocated and owned by the caller, so there is no need to free or release.

impl ImuSample {
    /// Extract accelerometer sample from `ImuSample`.
    ///
    /// **Return value:**
    /// * **[f32; 3]** containing accelerometer sample in meters per second squared with its components in XYZ order.
    pub fn get_acc(&self) -> [f32; 3] {
        unsafe {
            [
                self.handle.acc_sample.xyz.x,
                self.handle.acc_sample.xyz.y,
                self.handle.acc_sample.xyz.z,
            ]
        }
    }

    /// Extract X component of the accelerometer sample from `ImuSample`.
    ///
    /// **Return value:**
    /// * **f32** containing X component of the accelerometer sample in meters per second squared.
    pub fn get_acc_x(&self) -> f32 {
        unsafe { self.handle.acc_sample.xyz.x }
    }

    /// Extract Y component of the accelerometer sample from `ImuSample`.
    ///
    /// **Return value:**
    /// * **f32** containing Y component of the accelerometer sample in meters per second squared.
    pub fn get_acc_y(&self) -> f32 {
        unsafe { self.handle.acc_sample.xyz.y }
    }

    /// Extract Z component of the accelerometer sample from `ImuSample`.
    ///
    /// **Return value:**
    /// * **f32** containing Z component of the accelerometer sample in meters per second squared.
    pub fn get_acc_z(&self) -> f32 {
        unsafe { self.handle.acc_sample.xyz.z }
    }

    /// Extract gyroscope sample from `ImuSample`.
    ///
    /// **Return value:**
    /// * **[f32; 3]** containing gyroscope sample in radians per second with its components in XYZ order.
    pub fn get_gyro(&self) -> [f32; 3] {
        unsafe {
            [
                self.handle.gyro_sample.xyz.x,
                self.handle.gyro_sample.xyz.y,
                self.handle.gyro_sample.xyz.z,
            ]
        }
    }

    /// Extract X component of the gyroscope sample from `ImuSample`.
    ///
    /// **Return value:**
    /// * **f32** containing X component of the gyroscope sample in radians per second.
    pub fn get_gyro_x(&self) -> f32 {
        unsafe { self.handle.gyro_sample.xyz.x }
    }

    /// Extract Y component of the gyroscope sample from `ImuSample`.
    ///
    /// **Return value:**
    /// * **f32** containing Y component of the gyroscope sample in radians per second.
    pub fn get_gyro_y(&self) -> f32 {
        unsafe { self.handle.gyro_sample.xyz.y }
    }

    /// Extract Z component of the gyroscope sample from `ImuSample`.
    ///
    /// **Return value:**
    /// * **f32** containing Z component of the gyroscope sample in radians per second.
    pub fn get_gyro_z(&self) -> f32 {
        unsafe { self.handle.gyro_sample.xyz.z }
    }

    /// Extract timestamp of the accelerometer sample.
    ///
    /// **Return value:**
    /// * **u64** containing timestamp in microseconds.
    pub fn get_acc_timestamp(&self) -> u64 {
        self.handle.acc_timestamp_usec
    }

    /// Extract timestamp of the gyroscope sample.
    ///
    /// **Return value:**
    /// * **u64** containing timestamp in microseconds.
    pub fn get_gyro_timestamp(&self) -> u64 {
        self.handle.gyro_timestamp_usec
    }

    /// Extract temperature associated with the `ImuSample`.
    ///
    /// **Return value:**
    /// * **f32** containing temperature in Celsius.
    pub fn get_temperature(&self) -> f32 {
        self.handle.temperature
    }
}
