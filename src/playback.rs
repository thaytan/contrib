use k4a_sys::*;

use crate::calibration::Calibration;
use crate::capture::Capture;
use crate::error::{K4aError, Result};
use crate::imu_sample::ImuSample;
use std::convert::TryInto;

/// Struct representation [`Playback`](../playback/struct.Playback.html) that wraps around
/// `k4a_playback_t`, which is a handle to a recording opened for playback.
pub struct Playback {
    pub(crate) handle: k4a_playback_t,
}

/// Required for moving between threads
unsafe impl Send for Playback {}
unsafe impl Sync for Playback {}

/// Safe releasing of the `k4a_playback_t` handle.
impl Drop for Playback {
    fn drop(&mut self) {
        unsafe {
            k4a_playback_close(self.handle);
        }
    }
}

impl Playback {
    /// Open a [`Playback`](../playback/struct.Playback.html) track.
    ///
    /// # Arguments
    /// * `file_path` - Filesystem path of an existing recording.
    ///
    /// # Returns
    /// * `Ok(Playback)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn open(file_path: &String) -> Result<Playback> {
        let mut playback = Playback {
            handle: std::ptr::null_mut(),
        };
        match unsafe {
            k4a_playback_open(
                file_path.as_ptr() as *const std::os::raw::c_char,
                &mut playback.handle,
            )
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(playback),
            k4a_result_t::K4A_RESULT_FAILED => {
                Err(K4aError::Failure("File could not be opened for playback"))
            }
        }
    }

    /// Acquire [`Calibration`](../calibration/struct.Calibration.html) for the
    /// [`Device`](../device/struct.Device.html) used during recording.
    ///
    /// # Returns
    /// * `Ok(Calibration)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_calibration(&self) -> Result<Calibration> {
        let mut calibration_handle = k4a_calibration_t::default();
        match unsafe { k4a_playback_get_calibration(self.handle, &mut calibration_handle) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(Calibration {
                handle: calibration_handle,
            }),
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to acquire calibration data for the `Playback`",
            )),
        }
    }

    /// Acquire raw camera calibration for the [`Device`](../device/struct.Device.html) used during
    /// recording.
    ///
    /// # Returns
    /// * `Ok(&[u8])` containing the raw calibration data on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_raw_calibration(&self) -> Result<&[u8]> {
        let mut calibration_data_length: u64 = 0;
        match unsafe {
            k4a_playback_get_raw_calibration(
                self.handle,
                std::ptr::null_mut(),
                &mut calibration_data_length,
            )
        } {
            k4a_buffer_result_t::K4A_BUFFER_RESULT_TOO_SMALL => {}
            _ => {
                return Err(K4aError::Failure(
                    "Failed to acquire raw calibration data length",
                ))
            }
        }

        let mut calibration_data = vec![0_u8; calibration_data_length.try_into().unwrap()];
        match unsafe {
            k4a_playback_get_raw_calibration(
                self.handle,
                calibration_data.as_mut_ptr(),
                &mut calibration_data_length,
            )
        } {
            k4a_buffer_result_t::K4A_BUFFER_RESULT_SUCCEEDED => Ok(unsafe {
                std::slice::from_raw_parts(
                    calibration_data.as_mut_ptr(),
                    calibration_data_length.try_into().unwrap(),
                )
            }),
            _ => Err(K4aError::Failure("Failed to acquire raw calibration data")),
        }
    }

    /// Acquire the configuration for the [`Device`](../device/struct.Device.html) used during
    /// recording.
    ///
    /// # Returns
    /// * `Ok(RecordConfiguration)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_record_configuration(&self) -> Result<RecordConfiguration> {
        let mut configuration = RecordConfiguration::default();
        match unsafe { k4a_playback_get_record_configuration(self.handle, &mut configuration) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(configuration),
            k4a_result_t::K4A_RESULT_FAILED => {
                Err(K4aError::Failure("Failed to get `RecordConfiguration`"))
            }
        }
    }

    /// Acquire the value of a tag from a recording.
    ///
    /// # Arguments
    /// * `name` - The name of the tag to read.
    ///
    /// # Returns
    /// * `Ok(String)` containing the tag value on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_tag(&self, name: &String) -> Result<String> {
        let mut tag_length: u64 = 0;
        match unsafe {
            k4a_playback_get_tag(
                self.handle,
                name.as_ptr() as *const std::os::raw::c_char,
                std::ptr::null_mut(),
                &mut tag_length,
            )
        } {
            k4a_buffer_result_t::K4A_BUFFER_RESULT_TOO_SMALL => {}
            _ => {
                return Err(K4aError::Failure(
                    "Failed to acquire serial number length from `Playback`",
                ))
            }
        }

        let mut tag_value = vec![0_u8; tag_length.try_into().unwrap()];
        match unsafe {
            k4a_playback_get_tag(
                self.handle,
                name.as_ptr() as *const std::os::raw::c_char,
                tag_value.as_mut_ptr() as *mut std::os::raw::c_char,
                &mut tag_length,
            )
        } {
            k4a_buffer_result_t::K4A_BUFFER_RESULT_SUCCEEDED => {
                Ok(unsafe { String::from_utf8_unchecked(tag_value) })
            }
            _ => Err(K4aError::Failure(
                "Failed to acquire serial number from `Playback`",
            )),
        }
    }

    /// Set the image format that color captures will be converted to.
    ///
    /// # Arguments
    /// * `format` - The target format of the color [`Image`](../image/struct.Image.html) to be
    /// returned in captures.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn set_color_conversion(&self, format: ImageFormat) -> Result<()> {
        match unsafe { k4a_playback_set_color_conversion(self.handle, format) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(()),
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "`Playback` setting color conversion failed",
            )),
        }
    }

    /// Read the next [`Capture`](../capture/struct.Capture.html) in the recording sequence.
    ///
    /// # Returns
    /// * `Ok(Capture)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    /// * `Err(K4aError::Eos)` at the end of recording.
    pub fn get_next_capture(&self) -> Result<Capture> {
        let mut capture = Capture {
            handle: std::ptr::null_mut(),
        };
        match unsafe { k4a_playback_get_next_capture(self.handle, &mut capture.handle) } {
            k4a_stream_result_t::K4A_STREAM_RESULT_SUCCEEDED => Ok(capture),
            k4a_stream_result_t::K4A_STREAM_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to acquire next `Capture` from `Playback`",
            )),
            k4a_stream_result_t::K4A_STREAM_RESULT_EOF => Err(K4aError::Eof),
        }
    }

    /// Read the previous [`Capture`](../capture/struct.Capture.html) in the recording sequence.
    ///
    /// # Returns
    /// * `Ok(Capture)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    /// * `Err(K4aError::Eos)` at the beginning of recording.
    pub fn get_previous_capture(&self) -> Result<Capture> {
        let mut capture = Capture {
            handle: std::ptr::null_mut(),
        };
        match unsafe { k4a_playback_get_previous_capture(self.handle, &mut capture.handle) } {
            k4a_stream_result_t::K4A_STREAM_RESULT_SUCCEEDED => Ok(capture),
            k4a_stream_result_t::K4A_STREAM_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to acquire previous `Capture` from `Playback`",
            )),
            k4a_stream_result_t::K4A_STREAM_RESULT_EOF => Err(K4aError::Eof),
        }
    }

    /// Read the next [`ImuSample`](../imu_sample/struct.ImuSample.html) in the recording sequence.
    ///
    /// # Returns
    /// * `Ok(ImuSample)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    /// * `Err(K4aError::Eos)` at the end of recording.
    pub fn get_next_imu_sample(&self) -> Result<ImuSample> {
        let mut imu_sample_handle = k4a_imu_sample_t::default();
        match unsafe { k4a_playback_get_next_imu_sample(self.handle, &mut imu_sample_handle) } {
            k4a_stream_result_t::K4A_STREAM_RESULT_SUCCEEDED => Ok(ImuSample {
                handle: imu_sample_handle,
            }),
            k4a_stream_result_t::K4A_STREAM_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to acquire next `ImuSample` from `Playback`",
            )),
            k4a_stream_result_t::K4A_STREAM_RESULT_EOF => Err(K4aError::Eof),
        }
    }

    /// Read the previous [`ImuSample`](../imu_sample/struct.ImuSample.html) in the recording
    /// sequence.
    ///
    /// # Returns
    /// * `Ok(ImuSample)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    /// * `Err(K4aError::Eos)` at the beginning of recording.
    pub fn get_previous_imu_sample(&self) -> Result<ImuSample> {
        let mut imu_sample_handle = k4a_imu_sample_t::default();
        match unsafe { k4a_playback_get_previous_imu_sample(self.handle, &mut imu_sample_handle) } {
            k4a_stream_result_t::K4A_STREAM_RESULT_SUCCEEDED => Ok(ImuSample {
                handle: imu_sample_handle,
            }),
            k4a_stream_result_t::K4A_STREAM_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to acquire previous `ImuSample` from `Playback`",
            )),
            k4a_stream_result_t::K4A_STREAM_RESULT_EOF => Err(K4aError::Eof),
        }
    }

    /// Seek to a specific timestamp within a recording.
    ///
    /// # Arguments
    /// * `offset` - The timestamp offset to seek to relative to `origin` in microseconds.
    /// * `origin` - Specifies if the seek operation should be done relative to the beginning
    /// (`K4A_PLAYBACK_SEEK_BEGIN`) or end (`K4A_PLAYBACK_SEEK_END`) of the recording.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn seek_timestamp(&self, offset: i64, origin: PlaybackSeekOrigin) -> Result<()> {
        match unsafe { k4a_playback_seek_timestamp(self.handle, offset, origin) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(()),
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure("`Playback` seeking failed")),
        }
    }

    /// Gets the last timestamp in a recording. Can be used to determine the length of a recording.
    ///
    /// # Returns
    /// * `u64` containing the timestamp of the last [`Capture`](../capture/struct.Capture.html) or
    /// [`ImuSample`](../imu_sample/struct.ImuSample.html) in microseconds.
    pub fn get_last_timestamp(&self) -> u64 {
        unsafe { k4a_playback_get_last_timestamp_usec(self.handle) }
    }
}
