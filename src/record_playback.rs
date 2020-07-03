// License: MIT. See LICENSE file in root directory.
// Copyright(c) 2019 Aivero. All Rights Reserved.

use crate::device::Device;
use crate::error::Error;
use crate::pipeline_profile::PipelineProfile;

// Expose `rs2_camera_info` for external use.
pub use rs2::rs2_camera_info;

/// Struct representation of a [`Playback`](../record_playback/struct.Playback.html) that wraps
/// around `rs2_device` handle.
pub struct Playback {
    pub(crate) handle: *mut rs2::rs2_device,
}

impl Playback {
    /// Create [`Playback`](../record_playback/struct.Playback.html) from
    /// [`Device`](../device/struct.Device.html).
    ///
    /// # Arguments
    /// * `device` - A [`Device`](../device/struct.Device.html) to use for creation.
    ///
    /// # Returns
    /// * `Playback`
    pub fn create_from_device(device: &Device) -> Playback {
        Playback {
            handle: device.handle,
        }
    }

    /// Create [`Playback`](../record_playback/struct.Playback.html) from
    /// [`PipelineProfile`](../pipeline_profile/struct.PipelineProfile.html).
    ///
    /// # Arguments
    /// * `pipeline_profile` - A
    /// [`PipelineProfile`](../pipeline_profile/struct.PipelineProfile.html) to use for creation.
    ///
    /// connected device.
    /// # Returns
    /// * `Ok(Playback)` on success.
    /// * `Err(Error)` on failure.
    pub fn create_from_pipeline_profile(
        pipeline_profile: &PipelineProfile,
    ) -> Result<Playback, Error> {
        Ok(Playback {
            handle: pipeline_profile.get_device()?.handle,
        })
    }

    /// Set the [`Playback`](../record_playback/struct.Playback.html) to work in real time or non
    /// real time. In real time mode, [`Playback`](../record_playback/struct.Playback.html) will
    /// play the same way the file was recorded. In real time mode if the application takes too
    /// long to handle the callback, frames may be dropped. In non real time mode,
    /// [`Playback`](../record_playback/struct.Playback.html) will wait for each callback to finish
    /// handling the data before reading the next frame. In this mode no frames will be dropped,
    /// and the application controls the frame rate of the
    /// [`Playback`](../record_playback/struct.Playback.html) (according to the callback handler
    /// duration).
    ///
    /// # Arguments
    /// * `enable` - Set `true` for real time mode and `false` for non real time mode.
    ///
    /// connected device.
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(Error)` on failure.
    pub fn set_real_time(&self, enable: bool) -> Result<(), Error> {
        let mut error = Error::default();
        unsafe { rs2::rs2_playback_device_set_real_time(self.handle, enable as i32, error.inner()) }
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    /// Indicates if playback is in real time mode or non real time.
    ///
    /// connected device.
    /// # Returns
    /// * `Ok(bool)` on success, `true` for real time mode and `false` for non real time mode.
    /// * `Err(Error)` on failure.
    pub fn is_real_time(&self) -> Result<bool, Error> {
        let mut error = Error::default();
        let ret = unsafe { rs2::rs2_playback_device_is_real_time(self.handle, error.inner()) };
        if error.check() {
            Err(error)
        } else if ret == 0 {
            Ok(false)
        } else {
            Ok(true)
        }
    }

    // unimplemented!
}
