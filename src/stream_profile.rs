use crate::error::Error;
use rs2;

/// Struct representation of [`StreamProfile`](struct.StreamProfile.html) that wraps around 
/// `rs2_stream_profile` handle. The [`StreamProfile`](struct.StreamProfile.html) contains 
/// information about a specific stream.
pub struct StreamProfile {
    pub(crate) handle: *mut rs2::rs2_stream_profile,
}

/// Safe releasing of the `rs2_stream_profile` handle is required only if it is cloned.
impl Drop for StreamProfile {
    fn drop(&mut self) {
        // unsafe {
        //     rs2::rs2_delete_stream_profile(self.handle);
        // }
    }
}

/// Helper struct that contains data from [`StreamProfile`](struct.StreamProfile.html)
pub struct StreamData {
    pub stream: rs2::rs2_stream,
    pub format: rs2::rs2_format,
    pub index: i32,
    pub id: i32,
    pub framerate: i32,
}

/// Default constructor of `StreamData`.
impl Default for StreamData {
    fn default() -> Self {
        Self {
            stream: rs2::rs2_stream::RS2_STREAM_ANY,
            format: rs2::rs2_format::RS2_FORMAT_ANY,
            index: -1,
            id: 0,
            framerate: 0,
        }
    }
}

/// Helper struct that contains resolution from [`StreamProfile`](struct.StreamProfile.html)
#[derive(PartialEq, Clone)]
pub struct StreamResolution {
    pub width: i32,
    pub height: i32,
}

/// Default constructor of [`StreamProfile`](struct.StreamProfile.html).
impl Default for StreamResolution {
    fn default() -> Self {
        Self {
            width: -1,
            height: -1,
        }
    }
}

impl StreamProfile {
    /// Extract common parameters of a [`StreamProfile`](struct.StreamProfile.html).
    ///
    /// # Returns
    /// * `Ok(StreamData)` on success.
    /// * `Err(Error)` on failure.
    pub fn get_data(&self) -> Result<StreamData, Error> {
        let mut error = Error::default();
        let mut data = StreamData::default();
        unsafe {
            rs2::rs2_get_stream_profile_data(
                self.handle,
                &mut data.stream as *mut rs2::rs2_stream,
                &mut data.format as *mut rs2::rs2_format,
                &mut data.index as *mut i32,
                &mut data.id as *mut i32,
                &mut data.framerate as *mut i32,
                error.inner(),
            );
        }
        if error.check() {
            Err(error)
        } else {
            Ok(data)
        }
    }

    /// Extract resolution of the stream described by [`StreamProfile`](struct.StreamProfile.html).
    ///
    /// # Returns
    /// * `Ok(StreamResolution)` on success.
    /// * `Err(Error)` on failure.
    pub fn get_resolution(&self) -> Result<StreamResolution, Error> {
        let mut error = Error::default();
        let mut resolution = StreamResolution::default();
        unsafe {
            rs2::rs2_get_video_stream_resolution(
                self.handle,
                &mut resolution.width as *mut i32,
                &mut resolution.height as *mut i32,
                error.inner(),
            );
        }
        if error.check() {
            Err(error)
        } else {
            Ok(resolution)
        }
    }

    /// Obtain intrinsics of a [`StreamProfile`](struct.StreamProfile.html).
    ///
    /// # Returns
    /// * `Ok(rs2_intrinsics)` on success.
    /// * `Err(Error)` on failure.
    pub fn get_intrinsics(&self) -> Result<rs2::rs2_intrinsics, Error> {
        unimplemented!()
    }

    /// Obtain extrinsics between two [`StreamProfile`](struct.StreamProfile.html)s.
    ///    
    /// # Arguments
    /// * `from` - Origin [`StreamProfile`](struct.StreamProfile.html).
    /// * `to` - Target [`StreamProfile`](struct.StreamProfile.html).
    ///
    /// # Returns
    /// * `Ok(rs2_extrinsics)` on success.
    /// * `Err(Error)` on failure.
    pub fn get_extrinsics(_from: &Self, _to: &Self) -> Result<rs2::rs2_extrinsics, Error> {
        unimplemented!()
    }
}
