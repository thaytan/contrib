// License: MIT. See LICENSE file in root directory.
// Copyright(c) 2019 Aivero. All Rights Reserved.

use crate::error::Error;
use crate::stream_profile::StreamProfile;

/// Struct representation of [`Sensor`](../sensor/struct.Sensor.html) that wraps around
/// `rs2_sensor` handle.
pub struct Sensor {
    pub(crate) handle: *mut rs2::rs2_sensor,
}

/// Safe releasing of the `rs2_sensor` handle.
impl Drop for Sensor {
    fn drop(&mut self) {
        unsafe {
            rs2::rs2_delete_sensor(self.handle);
        }
    }
}

impl Sensor {
    /// Retrieve the [`StreamProfile`](../stream_profile/struct.StreamProfile.html)s of a
    /// [`Sensor`](../sensor/struct.Sensor.html).
    ///
    /// # Returns
    /// * `Ok(Vec<StreamProfile>)` on success.
    /// * `Err(Error)` on failure.
    pub fn get_stream_profiles(&self) -> Result<Vec<StreamProfile>, Error> {
        let mut error = Error::default();
        let profile_list = unsafe { rs2::rs2_get_stream_profiles(self.handle, error.inner()) };
        if error.check() {
            return Err(error);
        };
        let count = unsafe { rs2::rs2_get_stream_profiles_count(profile_list, error.inner()) };
        let mut res: Vec<StreamProfile> = Vec::new();
        for i in 0..count {
            res.push(StreamProfile {
                handle: unsafe {
                    rs2::rs2_get_stream_profile(profile_list, i, error.inner())
                        as *mut rs2::rs2_stream_profile
                },
            });
            if error.check() {
                return Err(error);
            };
        }
        Ok(res)
    }

    /// When called on a depth [`Sensor`](../sensor/struct.Sensor.html), this method will return
    /// the number of meters represented by a single depth unit
    ///
    /// # Returns
    /// * `Ok(f32)` on success.
    /// * `Err(Error)` on failure.
    pub fn get_depth_scale(&self) -> Result<f32, Error> {
        let mut error = Error::default();
        let depth_scale = unsafe { rs2::rs2_get_depth_scale(self.handle, error.inner()) };
        if error.check() {
            Err(error)
        } else {
            Ok(depth_scale)
        }
    }

    // unimplemented!
}
