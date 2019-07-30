use crate::error::Error;
use crate::stream::StreamProfile;

#[derive(Debug)]
pub struct Sensor {
    pub raw: *mut rs2::rs2_sensor,
}

impl Drop for Sensor {
    fn drop(&mut self) {
        unsafe {
            rs2::rs2_delete_sensor(self.raw);
        }
    }
}

impl Sensor {
    pub fn get_stream_profiles(&self) -> Result<Vec<StreamProfile>, Error> {
        let mut error = Error::default();
        let profile_list = unsafe { rs2::rs2_get_stream_profiles(self.raw, error.inner()) };
        if error.check() {
            return Err(error);
        };

        let count = unsafe { rs2::rs2_get_stream_profiles_count(profile_list, error.inner()) };
        let mut res: Vec<StreamProfile> = Vec::new();
        for i in 0..count {
            res.push(StreamProfile {
                raw: unsafe {
                    rs2::rs2_get_stream_profile(profile_list, i, error.inner())
                        as *mut rs2::rs2_stream_profile
                },
                clone: false,
            });
            if error.check() {
                return Err(error);
            };
        }
        Ok(res)
    }

    pub fn get_depth_scale(&self) -> Result<f32, Error> {
        let mut error = Error::default();

        let depth_scale;
        unsafe {
            depth_scale = rs2::rs2_get_depth_scale(self.raw, error.inner());
        }

        if error.check() {
            Err(Error::new("Failed to get depth scale"))
        } else {
            Ok(depth_scale)
        }
    }
}
