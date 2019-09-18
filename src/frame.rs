use crate::error::Error;
use crate::stream::StreamProfile;
use rs2;
use crate::util::to_string;
use std::collections::HashMap;

pub struct Frame {
    pub raw: *mut rs2::rs2_frame,
}

// impl Drop for Frame {
//     fn drop(&mut self) {
//         unsafe { rs2::rs2_release_frame(self.raw); }
//     }
// }

impl Frame {
    pub fn release(&self) {
        unsafe { rs2::rs2_release_frame(self.raw) };
    }

    pub fn get_frame_number(&self) -> Result<u64, Error> {
        let mut error = Error::default();
        let frame_number = unsafe { rs2::rs2_get_frame_number(self.raw, error.inner()) };
        if error.check() {
            Err(error)
        } else {
            Ok(frame_number)
        }
    }

    pub fn get_timestamp(&self) -> Result<f64, Error> {
        let mut error = Error::default();
        let timestamp = unsafe { rs2::rs2_get_frame_timestamp(self.raw, error.inner()) };
        if error.check() {
            Err(error)
        } else {
            Ok(timestamp)
        }
    }

    pub fn get_height(&self) -> Result<i32, Error> {
        let mut error = Error::default();
        let height = unsafe { rs2::rs2_get_frame_height(self.raw, error.inner()) };
        if error.check() {
            Err(error)
        } else {
            Ok(height)
        }
    }

    pub fn get_width(&self) -> Result<i32, Error> {
        let mut error = Error::default();
        let width = unsafe { rs2::rs2_get_frame_width(self.raw, error.inner()) };
        if error.check() {
            Err(error)
        } else {
            Ok(width)
        }
    }

    pub fn get_bits_per_pixel(&self) -> Result<i32, Error> {
        let mut error = Error::default();
        let bpp = unsafe { rs2::rs2_get_frame_bits_per_pixel(self.raw, error.inner()) };
        if error.check() {
            Err(error)
        } else {
            Ok(bpp)
        }
    }

    pub fn get_size(&self) -> Result<usize, Error> {
        let width = self.get_width()?;
        let height = self.get_height()?;
        let bits = self.get_bits_per_pixel()?;
        Ok((width * height * bits) as usize)
    }

    pub fn get_data(&self) -> Result<Vec<u8>, Error> {
        let mut error = Error::default();
        let size = self.get_size().unwrap();
        let data = unsafe {
            let data_ptr = rs2::rs2_get_frame_data(self.raw, error.inner());
            if error.check() {
                return Err(error);
            };
            std::slice::from_raw_parts(data_ptr as *const u8, (size / 8) as usize).to_vec()
        };
        Ok(data)
    }

    pub fn get_profile(&self) -> Result<StreamProfile, Error> {
        let mut error = Error::default();
        let profile = StreamProfile {
            raw: unsafe {
                rs2::rs2_get_frame_stream_profile(self.raw, error.inner())
                    as *mut rs2::rs2_stream_profile
            },
            clone: false,
        };
        if error.check() {
            Err(error)
        } else {
            Ok(profile)
        }
    }

    pub fn get_metadata(&self, frame: &Frame) -> Result<HashMap<String, i64>, Error> {
        let mut error = Error::default();
        let mut meta_values : HashMap<String, i64> = HashMap::new();

        for i in 0..rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_COUNT {
            // Cast the integer to a rs2_frame_metadata_value, which realsense uses to identify metadata fields
            let metadata_value : rs2::rs2_frame_metadata_value = i;
            // Check if the given index is supported, ignore it if not
            let meta_supported = unsafe { rs2::rs2_supports_frame_metadata(frame.raw, metadata_value, error.inner()) };
            if meta_supported == 0 || error.check() {
                continue;
            }
            // Attempt to get the meta's name and value
            let meta_name = unsafe { to_string(rs2::rs2_frame_metadata_to_string(metadata_value)) };
            let mete_val = unsafe { rs2::rs2_get_frame_metadata(frame.raw, metadata_value, error.inner()) };
            if error.check() {
                return Err(error);
            }

            // Append that to the dictionary
            meta_values.insert(meta_name, mete_val);
        }
        Ok(meta_values)
    }
}
