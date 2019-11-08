use crate::device::Device;
use crate::error::Error;
use crate::stream_profile::StreamProfile;
use rs2;

/// Struct representation of `Pipeline` that wraps around `rs2_pipeline_profile` handle.
pub struct PipelineProfile {
    pub(crate) handle: *mut rs2::rs2_pipeline_profile,
}

/// Safe releasing of the `rs2_pipeline_profile` handle.
impl Drop for PipelineProfile {
    fn drop(&mut self) {
        unsafe {
            rs2::rs2_delete_pipeline_profile(self.handle);
        }
    }
}

// TODO: Make sure these are required, and if so, implement them properly
unsafe impl Send for PipelineProfile {}
unsafe impl Sync for PipelineProfile {}

impl PipelineProfile {
    /// Retrieve the `Device` used by the `Pipeline`. The `Device` class provides the application
    /// access to control camera additional settings - get `Device` information, sensor options
    /// information, options value query and set, sensor specific extensions. Since the `Pipeline`
    /// controls the `Device` streams configuration, activation state and frames reading, calling
    /// the `Device` API functions, which execute those operations, results in unexpected behavior.
    /// The `Pipeline` streaming `Device` is selected during `Pipeline::start()`. `Device`s of
    /// profiles, which are not returned by `Pipeline::start()` or `Pipeline::get_active_profile()`,
    ///  are not guaranteed to be used by the `Pipeline`.
    ///
    /// **Return value:**
    /// * **Ok(Device)** on success.
    /// * **Err(Error)** on failure.
    pub fn get_device(&self) -> Result<Device, Error> {
        let mut error = Error::default();
        let device = Device {
            handle: unsafe { rs2::rs2_pipeline_profile_get_device(self.handle, error.inner()) },
        };
        if error.check() {
            Err(error)
        } else {
            Ok(device)
        }
    }

    /// Retrieve the selected `StreamProfile`s, which are enabled in this `PipelineProfile`.
    ///
    /// **Return value:**
    /// * **Ok(Vec<StreamProfile>)** on success.
    /// * **Err(Error)** on failure.
    pub fn get_streams(&self) -> Result<Vec<StreamProfile>, Error> {
        let mut error = Error::default();
        unsafe {
            let stream_profiles = rs2::rs2_pipeline_profile_get_streams(self.handle, error.inner());
            if error.check() {
                return Err(error);
            };
            let stream_count = rs2::rs2_get_stream_profiles_count(stream_profiles, error.inner());
            if error.check() {
                return Err(error);
            };
            let mut streams: Vec<StreamProfile> = Vec::new();
            for i in 0..stream_count {
                streams.push(StreamProfile {
                    handle: rs2::rs2_get_stream_profile(stream_profiles, i, error.inner())
                        as *mut rs2::rs2_stream_profile,
                });
                if error.check() {
                    return Err(error);
                };
            }
            Ok(streams)
        }
    }

    /// Retrieve the `StreamProfile` that is enabled for the specified `Stream` in this
    /// `PipelineProfile`.
    ///
    /// **Parameters:**
    /// * **stream_type** - Stream type of the desired profile.
    /// * **stream_index** - Stream index of the desired profile, with -1 for any matching.
    ///
    /// **Return value:**
    /// * **Ok(StreamProfile)** on success if such stream exist.
    /// * **Ok(None)** on success if no such stream exists.
    /// * **Err(Error)** on failure.
    pub fn get_stream(
        &self,
        stream_type: rs2::rs2_stream,
        stream_index: i32,
    ) -> Result<Option<StreamProfile>, Error> {
        for stream in self.get_streams()? {
            let stream_data = stream.get_data()?;
            if stream_data.stream == stream_type {
                if stream_index != -1 && stream_data.index == stream_index {
                    return Ok(Some(stream));
                }
            }
        }
        Ok(None)
    }
}
