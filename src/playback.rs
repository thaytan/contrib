use crate::calibration::Calibration;
use crate::capture::Capture;
use crate::imu_sample::ImuSample;
use k4a_sys::*;

/// Struct representation `Playback` that wraps around `k4a_playback_t`, which is a handle to a recording opened for playback.
pub struct Playback {
    pub(crate) handle: k4a_playback_t,
}

// Safe releasing of the `k4a_playback_t` handle.
impl Drop for Playback {
    fn drop(&mut self) {
        unsafe {
            k4a_playback_close(self.handle);
        }
    }
}

impl Playback {
    /// Open a playback track.
    ///
    /// **Parameter:**
    /// * **file_path** - Filesystem path of an existing recording.
    ///
    /// **Return value:**
    /// * **Ok(Playback)** on success.
    /// * **Err(&str)** on failure.
    pub fn open(file_path: String) -> Result<Playback, &'static str> {
        let playback_handle = std::ptr::null_mut();
        match unsafe { k4a_playback_open(file_path.as_ptr() as *const i8, playback_handle) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(Playback {
                handle: playback_handle as k4a_playback_t,
            }),
            k4a_result_t::K4A_RESULT_FAILED => Err("File could not be opened for playback"),
        }
    }

    /// Acquire `Calibration` for the `Device` used during recording.
    ///
    /// **Return value:**
    /// * **Ok(Calibration)** on success.
    /// * **Err(&str)** on failure.
    pub fn get_calibration(&self) -> Result<Calibration, &'static str> {
        let mut calibration_handle = k4a_calibration_t::default();
        match unsafe { k4a_playback_get_calibration(self.handle, &mut calibration_handle) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(Calibration {
                handle: calibration_handle,
            }),
            k4a_result_t::K4A_RESULT_FAILED => {
                Err("Failed to acquire calibration data for the device")
            }
        }
    }

    /// Acquire raw camera calibration for the `Device` used during recording.
    ///
    /// **Return value:**
    /// * **Ok(&[u8])** containing the raw calibration data on success.
    /// * **Err(&str)** on failure.
    pub fn get_raw_calibration(&self) -> Result<&[u8], &'static str> {
        let mut calibration_data_length = 0;
        match unsafe {
            k4a_playback_get_raw_calibration(
                self.handle,
                std::ptr::null_mut(),
                &mut calibration_data_length,
            )
        } {
            k4a_buffer_result_t::K4A_BUFFER_RESULT_TOO_SMALL => {}
            _ => return Err("Failed to acquire raw calibration data length"),
        }

        let mut calibration_data: Vec<u8> = Vec::with_capacity(calibration_data_length);
        match unsafe {
            k4a_playback_get_raw_calibration(
                self.handle,
                calibration_data.as_mut_ptr(),
                &mut calibration_data_length,
            )
        } {
            k4a_buffer_result_t::K4A_BUFFER_RESULT_SUCCEEDED => Ok(unsafe {
                std::slice::from_raw_parts(calibration_data.as_mut_ptr(), calibration_data_length)
            }),
            _ => Err("Failed to acquire raw calibration data"),
        }
    }

    /// Acquire the configuration for the `Device` used during recording.
    ///
    /// **Return value:**
    /// * **Ok(RecordConfiguration)** on success.
    /// * **Err(&str)** on failure.
    pub fn get_record_configuration(&self) -> Result<RecordConfiguration, &'static str> {
        let mut configuration = RecordConfiguration::default();
        match unsafe { k4a_playback_get_record_configuration(self.handle, &mut configuration) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(configuration),
            k4a_result_t::K4A_RESULT_FAILED => Err("Failed to get `RecordConfiguration`"),
        }
    }

    /// Acquire the value of a tag from a recording.
    ///
    /// **Parameter:**
    /// * **name** - The name of the tag to read.
    ///
    /// **Return value:**
    /// * **Ok(String)** containing the tag value on success.
    /// * **Err(&str)** on failure.
    pub fn get_tag(&self, name: String) -> Result<String, &'static str> {
        let mut tag_length = 0;
        match unsafe {
            k4a_playback_get_tag(
                self.handle,
                name.as_ptr() as *const i8,
                std::ptr::null_mut(),
                &mut tag_length,
            )
        } {
            k4a_buffer_result_t::K4A_BUFFER_RESULT_TOO_SMALL => {}
            _ => return Err("Failed to acquire serial number length"),
        }

        let mut tag_value = String::with_capacity(tag_length);
        match unsafe {
            k4a_playback_get_tag(
                self.handle,
                name.as_ptr() as *const i8,
                tag_value.as_mut_ptr() as *mut i8,
                &mut tag_length,
            )
        } {
            k4a_buffer_result_t::K4A_BUFFER_RESULT_SUCCEEDED => Ok(tag_value),
            _ => Err("Failed to acquire serial number"),
        }
    }

    /// Set the image format that color captures will be converted to.
    ///
    /// **Parameter:**
    /// * **format** - The target format of the color `Image` to be returned in captures.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(&str)** on failure.
    pub fn set_color_conversion(&self, format: k4a_image_format_t) -> Result<(), &'static str> {
        match unsafe { k4a_playback_set_color_conversion(self.handle, format) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(()),
            k4a_result_t::K4A_RESULT_FAILED => Err("Playback seeking failed"),
        }
    }

    /// Read the next `Capture` in the recording sequence.
    ///
    /// **Return value:**
    /// * **Ok(Capture)** on success.
    /// * **Err(k4a_stream_result_t)** on failure, indicating either `K4A_STREAM_RESULT_FAILED` or `K4A_STREAM_RESULT_EOF` if end of the recording is reached.
    pub fn get_next_capture(&self) -> Result<Capture, k4a_stream_result_t> {
        let capture_handle = std::ptr::null_mut();
        match unsafe { k4a_playback_get_next_capture(self.handle, capture_handle) } {
            k4a_stream_result_t::K4A_STREAM_RESULT_SUCCEEDED => Ok(Capture {
                handle: capture_handle as k4a_capture_t,
            }),
            k4a_stream_result_t::K4A_STREAM_RESULT_FAILED => {
                Err(k4a_stream_result_t::K4A_STREAM_RESULT_FAILED)
            }
            k4a_stream_result_t::K4A_STREAM_RESULT_EOF => {
                Err(k4a_stream_result_t::K4A_STREAM_RESULT_FAILED)
            }
        }
    }

    /// Read the previous `Capture` in the recording sequence.
    ///
    /// **Return value:**
    /// * **Ok(Capture)** on success.
    /// * **Err(k4a_stream_result_t)** on failure, indicating either `K4A_STREAM_RESULT_FAILED` or `K4A_STREAM_RESULT_EOF` if beginning of the recording is reached.
    pub fn get_previous_capture(&self) -> Result<Capture, k4a_stream_result_t> {
        let capture_handle = std::ptr::null_mut();
        match unsafe { k4a_playback_get_previous_capture(self.handle, capture_handle) } {
            k4a_stream_result_t::K4A_STREAM_RESULT_SUCCEEDED => Ok(Capture {
                handle: capture_handle as k4a_capture_t,
            }),
            k4a_stream_result_t::K4A_STREAM_RESULT_FAILED => {
                Err(k4a_stream_result_t::K4A_STREAM_RESULT_FAILED)
            }
            k4a_stream_result_t::K4A_STREAM_RESULT_EOF => {
                Err(k4a_stream_result_t::K4A_STREAM_RESULT_FAILED)
            }
        }
    }

    /// Read the next `ImuSample` in the recording sequence.
    ///
    /// **Return value:**
    /// * **Ok(ImuSample)** on success.
    /// * **Err(k4a_stream_result_t)** on failure, indicating either `K4A_STREAM_RESULT_FAILED` or `K4A_STREAM_RESULT_EOF` if end of the recording is reached.
    pub fn get_next_imu_sample(&self) -> Result<ImuSample, k4a_stream_result_t> {
        let mut imu_sample_handle = k4a_imu_sample_t::default();
        match unsafe { k4a_playback_get_next_imu_sample(self.handle, &mut imu_sample_handle) } {
            k4a_stream_result_t::K4A_STREAM_RESULT_SUCCEEDED => Ok(ImuSample {
                handle: imu_sample_handle,
            }),
            k4a_stream_result_t::K4A_STREAM_RESULT_FAILED => {
                Err(k4a_stream_result_t::K4A_STREAM_RESULT_FAILED)
            }
            k4a_stream_result_t::K4A_STREAM_RESULT_EOF => {
                Err(k4a_stream_result_t::K4A_STREAM_RESULT_FAILED)
            }
        }
    }

    /// Read the previous `ImuSample` in the recording sequence.
    ///
    /// **Return value:**
    /// * **Ok(ImuSample)** on success.
    /// * **Err(k4a_stream_result_t)** on failure, indicating either `K4A_STREAM_RESULT_FAILED` or `K4A_STREAM_RESULT_EOF` if beginning of the recording is reached.
    pub fn get_previous_imu_sample(&self) -> Result<ImuSample, k4a_stream_result_t> {
        let mut imu_sample_handle = k4a_imu_sample_t::default();
        match unsafe { k4a_playback_get_previous_imu_sample(self.handle, &mut imu_sample_handle) } {
            k4a_stream_result_t::K4A_STREAM_RESULT_SUCCEEDED => Ok(ImuSample {
                handle: imu_sample_handle,
            }),
            k4a_stream_result_t::K4A_STREAM_RESULT_FAILED => {
                Err(k4a_stream_result_t::K4A_STREAM_RESULT_FAILED)
            }
            k4a_stream_result_t::K4A_STREAM_RESULT_EOF => {
                Err(k4a_stream_result_t::K4A_STREAM_RESULT_FAILED)
            }
        }
    }

    /// Seek to a specific timestamp within a recording.
    ///
    /// **Parameters:**
    /// * **offset** - The timestamp offset to seek to relative to `origin` in microseconds.
    /// * **origin** - Specifies if the seek operation should be done relative to the beginning (`K4A_PLAYBACK_SEEK_BEGIN`) or end (`K4A_PLAYBACK_SEEK_END`) of the recording.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(&str)** on failure.
    pub fn seek_timestamp(
        &self,
        offset: i64,
        origin: k4a_playback_seek_origin_t,
    ) -> Result<(), &'static str> {
        match unsafe { k4a_playback_seek_timestamp(self.handle, offset, origin) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(()),
            k4a_result_t::K4A_RESULT_FAILED => Err("Playback seeking failed"),
        }
    }

    /// Gets the last timestamp in a recording. Can be used to determine the length of a recording.
    ///
    /// **Return value:**
    /// * **u64** containing the timestamp of the last `capture` or `ImuSample` in microseconds..
    pub fn get_last_timestamp(&self) -> u64 {
        unsafe { k4a_playback_get_last_timestamp_usec(self.handle) }
    }
}
