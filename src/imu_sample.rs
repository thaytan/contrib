use libk4a_sys::*;

/// Struct representation of [`ImuSample`](../imu_sample/struct.ImuSample.html) that wraps around
/// `k4a_imu_sample_t`, which manages an IMU buffer and associated metadata.
pub struct ImuSample {
    pub(crate) handle: k4a_imu_sample_t,
}

// The memory the `k4a_imu_sample` is written to is allocated and owned by the caller, so there is
// no need to free or release.

/// A helper struct for acquiring 3D data from [`ImuSample`](../imu_sample/struct.ImuSample.html).
pub struct VectorXYZ<T> {
    /// X component of the vector.
    pub x: T,
    /// Y component of the vector.
    pub y: T,
    /// Z component of the vector.
    pub z: T,
}

impl ImuSample {
    /// Extract accelerometer sample from [`ImuSample`](../imu_sample/struct.ImuSample.html).
    ///
    /// # Returns
    /// * `VectorXYZ<f32>` containing accelerometer sample in meters per second squared.
    pub fn get_acc(&self) -> VectorXYZ<f32> {
        unsafe {
            VectorXYZ {
                x: self.handle.acc_sample.xyz.x,
                y: self.handle.acc_sample.xyz.y,
                z: self.handle.acc_sample.xyz.z,
            }
        }
    }

    /// Extract X component of the accelerometer sample from
    /// [`ImuSample`](../imu_sample/struct.ImuSample.html).
    ///
    /// # Returns
    /// * `f32` containing X component of the accelerometer sample in meters per second squared.
    pub fn get_acc_x(&self) -> f32 {
        unsafe { self.handle.acc_sample.xyz.x }
    }

    /// Extract Y component of the accelerometer sample from
    /// [`ImuSample`](../imu_sample/struct.ImuSample.html).
    ///
    /// # Returns
    /// * `f32` containing Y component of the accelerometer sample in meters per second squared.
    pub fn get_acc_y(&self) -> f32 {
        unsafe { self.handle.acc_sample.xyz.y }
    }

    /// Extract Z component of the accelerometer sample from
    /// [`ImuSample`](../imu_sample/struct.ImuSample.html).
    ///
    /// # Returns
    /// * `f32` containing Z component of the accelerometer sample in meters per second squared.
    pub fn get_acc_z(&self) -> f32 {
        unsafe { self.handle.acc_sample.xyz.z }
    }

    /// Extract gyroscope sample from [`ImuSample`](../imu_sample/struct.ImuSample.html).
    ///
    /// # Returns
    /// * `VectorXYZ<f32>` containing gyroscope sample in radians per second.
    pub fn get_gyro(&self) -> VectorXYZ<f32> {
        unsafe {
            VectorXYZ {
                x: self.handle.gyro_sample.xyz.x,
                y: self.handle.gyro_sample.xyz.y,
                z: self.handle.gyro_sample.xyz.z,
            }
        }
    }

    /// Extract X component of the gyroscope sample from
    /// [`ImuSample`](../imu_sample/struct.ImuSample.html).
    ///
    /// # Returns
    /// * `f32` containing X component of the gyroscope sample in radians per second.
    pub fn get_gyro_x(&self) -> f32 {
        unsafe { self.handle.gyro_sample.xyz.x }
    }

    /// Extract Y component of the gyroscope sample from
    /// [`ImuSample`](../imu_sample/struct.ImuSample.html).
    ///
    /// # Returns
    /// * `f32` containing Y component of the gyroscope sample in radians per second.
    pub fn get_gyro_y(&self) -> f32 {
        unsafe { self.handle.gyro_sample.xyz.y }
    }

    /// Extract Z component of the gyroscope sample from
    /// [`ImuSample`](../imu_sample/struct.ImuSample.html).
    ///
    /// # Returns
    /// * `f32` containing Z component of the gyroscope sample in radians per second.
    pub fn get_gyro_z(&self) -> f32 {
        unsafe { self.handle.gyro_sample.xyz.z }
    }

    /// Extract timestamp of the accelerometer sample.
    ///
    /// # Returns
    /// * `u64` containing timestamp in microseconds.
    pub fn get_acc_timestamp(&self) -> u64 {
        self.handle.acc_timestamp_usec
    }

    /// Extract timestamp of the gyroscope sample.
    ///
    /// # Returns
    /// * `u64` containing timestamp in microseconds.
    pub fn get_gyro_timestamp(&self) -> u64 {
        self.handle.gyro_timestamp_usec
    }

    /// Extract temperature associated with the [`ImuSample`](../imu_sample/struct.ImuSample.html).
    ///
    /// # Returns
    /// * `f32` containing temperature in Celsius.
    pub fn get_temperature(&self) -> f32 {
        self.handle.temperature
    }
}
