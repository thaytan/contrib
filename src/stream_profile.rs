use crate::error::Error;
use rs2;

/// Struct representation of `StreamProfile` that wraps around `rs2_stream_profile` handle. The
/// `StreamProfile` contains information about a specific `Stream`.
pub struct StreamProfile {
    pub(crate) handle: *mut rs2::rs2_stream_profile,
}

// TODO: Make sure to release if cloning is implemented.
/// Safe releasing of the `rs2_stream_profile` handle is required only if it is cloned.
impl Drop for StreamProfile {
    fn drop(&mut self) {
        // unsafe {
        //     rs2::rs2_delete_stream_profile(self.handle);
        // }
    }
}

// TODO: Make sure these are required, and if so, implement them properly
unsafe impl Send for StreamProfile {}
unsafe impl Sync for StreamProfile {}

/// Helper struct that contains data from `StreamProfile`
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

/// Helper struct that contains resolution from `StreamProfile`
pub struct StreamResolution {
    pub width: i32,
    pub height: i32,
}

/// Default constructor of `StreamProfile`.
impl Default for StreamResolution {
    fn default() -> Self {
        Self {
            width: -1,
            height: -1,
        }
    }
}

impl StreamProfile {
    /// Extract common parameters of a `StreamProfile`.
    ///
    /// **Return value:**
    /// * **Ok(StreamData)** on success.
    /// * **Err(Error)** on failure.
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

    /// Extract resolution of the `Stream` described by `StreamProfile`.
    ///
    /// **Return value:**
    /// * **Ok(StreamResolution)** on success.
    /// * **Err(Error)** on failure.
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

    /// Obtain intrinsics of a `StreamProfile`.
    ///
    /// **Return value:**
    /// * **Ok(rs2_intrinsics)** on success.
    /// * **Err(Error)** on failure.
    pub fn get_intrinsics(&self) -> Result<rs2::rs2_intrinsics, Error> {
        unimplemented!()
    }

    /// Obtain extrinsics between two `StreamProfile`s.
    ///    
    /// **Parameters:**
    /// **from** - Origin `StreamProfile`.
    /// **to** - Target `StreamProfile`.
    ///
    /// **Return value:**
    /// * **Ok(rs2_extrinsics)** on success.
    /// * **Err(Error)** on failure.
    pub fn get_extrinsics(_from: &Self, _to: &Self) -> Result<rs2::rs2_extrinsics, Error> {
        unimplemented!()
    }
}
