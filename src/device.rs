use crate::calibration::Calibration;
use crate::capture::Capture;
use crate::imu_sample::ImuSample;
use k4a_sys::*;

/// Struct representation of a single *Azure Kinect DK (K4A)* `Device` that wraps around `k4a_device_t`.
pub struct Device {
    pub(crate) handle: k4a_device_t,
}

// Safe releasing of the `k4a_device_t` handle.
impl Drop for Device {
    fn drop(&mut self) {
        unsafe {
            k4a_device_close(self.handle);
        }
    }
}

impl Device {
    /// Determine number of connected devices.
    ///
    /// **Return value:**
    /// * Number of connected devices (**u32**) on success.
    /// * **Err(&str)** if no device is connected.
    pub fn get_number_of_connected_devices() -> Result<u32, &'static str> {
        let device_count = unsafe { k4a_device_get_installed_count() };
        if device_count == 0 {
            Err("No `Device` detected")
        } else {
            Ok(device_count)
        }
    }

    /// Open a `Device`.
    ///
    /// **Parameter:**
    /// * **index** - Index of the device. Pass **0_u32** if only one device is connected.
    ///
    /// **Return value:**
    /// * **Ok(Device)** on success.
    /// * **Err(&str)** on failure.
    pub fn open_device(index: u32) -> Result<Device, &'static str> {
        let device_count = Self::get_number_of_connected_devices()?;
        if (index + 1) < device_count {
            return Err("`Device` with the given index is not connected");
        }

        let device_handle = std::ptr::null_mut();
        match unsafe { k4a_device_open(index, device_handle) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(Device {
                handle: device_handle as k4a_device_t,
            }),
            k4a_result_t::K4A_RESULT_FAILED => Err("`Device` could not be opened"),
        }
    }

    /// Acquire serial number of a `Device`.
    ///
    /// **Return value:**
    /// * **Ok(String)** containing the serial number on success.
    /// * **Err(&str)** on failure.
    pub fn get_serial_number(&self) -> Result<String, &'static str> {
        let mut serial_number_length = 0;
        match unsafe {
            k4a_device_get_serialnum(self.handle, std::ptr::null_mut(), &mut serial_number_length)
        } {
            k4a_buffer_result_t::K4A_BUFFER_RESULT_TOO_SMALL => {}
            _ => return Err("Failed to acquire serial number length for `Device`"),
        }

        let mut serial_number = String::with_capacity(serial_number_length);
        match unsafe {
            k4a_device_get_serialnum(
                self.handle,
                serial_number.as_mut_ptr() as *mut i8,
                &mut serial_number_length,
            )
        } {
            k4a_buffer_result_t::K4A_BUFFER_RESULT_SUCCEEDED => Ok(serial_number),
            _ => Err("Failed to acquire serial number for `Device`"),
        }
    }

    /// Acquire serial number of each connected `Device`.
    ///
    /// **Return value:**
    /// * **Ok(<Vec<String>)** containing all serial numbers on success.
    /// * **Err(&str)** on failure.
    pub fn get_connected_serial_numbers() -> Result<Vec<String>, &'static str> {
        let device_count = Self::get_number_of_connected_devices()?;
        let mut serial_numbers: Vec<String> = Vec::with_capacity(device_count as usize);
        for index in 0..device_count {
            let mut device = Device {
                handle: std::ptr::null_mut(),
            };
            match unsafe { k4a_device_open(index, &mut device.handle) } {
                k4a_result_t::K4A_RESULT_SUCCEEDED => {
                    serial_numbers.push(device.get_serial_number()?)
                }
                _ => {}
            }
        }
        Ok(serial_numbers)
    }

    /// Open a `Device` with the corresponding serial number.
    ///
    /// **Parameter:**
    /// * **serial** - Serial number of the `Device`.
    ///
    /// **Return value:**
    /// * **Ok(Device)** on success.
    /// * **Err(&str)** on failure.
    pub fn open_device_with_serial(serial: &String) -> Result<Device, &'static str> {
        for index in 0..Self::get_number_of_connected_devices()? {
            let mut device = Device {
                handle: std::ptr::null_mut(),
            };
            match unsafe { k4a_device_open(index, &mut device.handle) } {
                k4a_result_t::K4A_RESULT_SUCCEEDED => {}
                k4a_result_t::K4A_RESULT_FAILED => continue,
            }
            if &device.get_serial_number()? == serial {
                return Ok(device);
            }
        }
        Err("`Device` with given serial is not detected")
    }

    /// Start cameras of a `Device`.
    ///
    /// **Parameter:**
    /// * **configuration** - Device configuration parameters for the cameras.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(&str)** on failure.
    pub fn start_cameras(
        &self,
        configuration: &mut DeviceConfiguration,
    ) -> Result<(), &'static str> {
        match unsafe { k4a_device_start_cameras(self.handle, configuration) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(()),
            k4a_result_t::K4A_RESULT_FAILED => Err("Cameras could not be started"),
        }
    }

    /// Stop the cameras of `Device`.
    pub fn stop_cameras(&self) {
        unsafe { k4a_device_stop_cameras(self.handle) }
    }

    /// Receive a `Capture` from a `Device`.
    ///
    /// **Parameter:**
    /// * **timeout** - Timeout in milliseconds.
    ///
    /// **Return value:**
    /// * **Ok(Capture)** on success.
    /// * **Err(k4a_wait_result_t)** on failure. Timeout is indicated by `K4A_WAIT_RESULT_TIMEOUT`, whereas other failure results in `K4A_WAIT_RESULT_FAILED`.
    pub fn get_capture(&self, timeout: i32) -> Result<Capture, k4a_wait_result_t> {
        let capture_handle = std::ptr::null_mut();
        match unsafe { k4a_device_get_capture(self.handle, capture_handle, timeout) } {
            k4a_wait_result_t::K4A_WAIT_RESULT_SUCCEEDED => Ok(Capture {
                handle: capture_handle as k4a_capture_t,
            }),
            k4a_wait_result_t::K4A_WAIT_RESULT_TIMEOUT => {
                Err(k4a_wait_result_t::K4A_WAIT_RESULT_TIMEOUT)
            }
            k4a_wait_result_t::K4A_WAIT_RESULT_FAILED => {
                Err(k4a_wait_result_t::K4A_WAIT_RESULT_FAILED)
            }
        }
    }

    /// Start IMU of a `Device`.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(&str)** on failure.
    pub fn start_imu(&self) -> Result<(), &'static str> {
        match unsafe { k4a_device_start_imu(self.handle) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(()),
            k4a_result_t::K4A_RESULT_FAILED => Err("IMU could not be started"),
        }
    }

    /// Stop IMU of `Device`.
    pub fn stop_imu(&self) {
        unsafe { k4a_device_stop_imu(self.handle) }
    }

    /// Receive an `ImuSample` from a `Device`.
    /// > Note that IMU samples are generated at a higher frequency than images, so it is possible to acquire more samples from queue in between two `Capture` samples.
    ///
    /// **Parameter:**
    /// * **timeout** - Timeout in milliseconds. To retrieve all the currently queued samples, call the function with `timeout` of 0 in a loop until the function returns **Err(&str)**.
    ///
    /// **Return value:**
    /// * **Ok(Capture)** on success.
    /// * **Err(k4a_wait_result_t)** on failure. Timeout is indicated by `K4A_WAIT_RESULT_TIMEOUT`, whereas other failure results in `K4A_WAIT_RESULT_FAILED`.
    pub fn get_imu_sample(&self, timeout: i32) -> Result<ImuSample, k4a_wait_result_t> {
        let mut imu_sample_handle = k4a_imu_sample_t::default();
        match unsafe { k4a_device_get_imu_sample(self.handle, &mut imu_sample_handle, timeout) } {
            k4a_wait_result_t::K4A_WAIT_RESULT_SUCCEEDED => Ok(ImuSample {
                handle: imu_sample_handle,
            }),
            k4a_wait_result_t::K4A_WAIT_RESULT_TIMEOUT => {
                Err(k4a_wait_result_t::K4A_WAIT_RESULT_TIMEOUT)
            }
            k4a_wait_result_t::K4A_WAIT_RESULT_FAILED => {
                Err(k4a_wait_result_t::K4A_WAIT_RESULT_FAILED)
            }
        }
    }

    /// Retrieve mode of color control `command` and value of mode is set to `K4A_COLOR_CONTROL_MODE_MANUAL`.
    ///
    /// **Parameter:**
    /// * **command** - Field to read from.
    ///
    /// **Return value:**
    /// * **Ok(Some(i32))** on success. It contains the `command` value if mode is set to `K4A_COLOR_CONTROL_MODE_MANUAL`.
    /// * **Ok(None)** on success if mode is set to `K4A_COLOR_CONTROL_MODE_AUTO`.
    /// * **Err(&str)** on failure.
    pub fn get_color_control(
        &self,
        command: k4a_color_control_command_t,
    ) -> Result<Option<i32>, &'static str> {
        let mut mode = k4a_color_control_mode_t::K4A_COLOR_CONTROL_MODE_AUTO;
        let mut value: i32 = 0;
        match unsafe { k4a_device_get_color_control(self.handle, command, &mut mode, &mut value) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(match mode {
                k4a_color_control_mode_t::K4A_COLOR_CONTROL_MODE_AUTO => None,
                k4a_color_control_mode_t::K4A_COLOR_CONTROL_MODE_MANUAL => Some(value),
            }),
            k4a_result_t::K4A_RESULT_FAILED => Err("Failed to acquire color sensor control value"),
        }
    }

    /// This function is NOT implemented!
    pub fn get_color_control_capabilities(&self) {
        unimplemented!()
    }

    /// Set `command` to `K4A_COLOR_CONTROL_MODE_MANUAL` mode with the specified `value`.
    ///
    /// **Parameters:**
    /// * **command** - Field to modify.
    /// * **value** - Value to set the `command` to.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(&str)** on failure.
    pub fn set_color_control_manual(
        &self,
        command: k4a_color_control_command_t,
        value: &i32,
    ) -> Result<(), &'static str> {
        match unsafe {
            k4a_device_get_color_control(
                self.handle,
                command,
                &mut k4a_color_control_mode_t::K4A_COLOR_CONTROL_MODE_MANUAL,
                &mut value.clone(),
            )
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(()),
            k4a_result_t::K4A_RESULT_FAILED => Err(
                "Failed to set color sensor control command to manual mode with a specified value",
            ),
        }
    }

    /// Set `command` to `K4A_COLOR_CONTROL_MODE_AUTO` mode.
    ///
    /// **Parameter:**
    /// * **command** - Field to modify.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(&str)** on failure.
    pub fn set_color_control_auto(
        &self,
        command: k4a_color_control_command_t,
    ) -> Result<(), &'static str> {
        match unsafe {
            k4a_device_get_color_control(
                self.handle,
                command,
                &mut k4a_color_control_mode_t::K4A_COLOR_CONTROL_MODE_AUTO,
                &mut 0,
            )
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(()),
            k4a_result_t::K4A_RESULT_FAILED => {
                Err("Failed to set color sensor control command to automatic mode")
            }
        }
    }

    /// Acquire `Calibration` for the `Device`.
    ///
    /// **Parameters:**
    /// * **depth_mode** - Mode of the depth camera.
    /// * **color_resolution** - Resolution of the color camera.
    ///
    /// **Return value:**
    /// * **Ok(Calibration)** on success.
    /// * **Err(&str)** on failure.
    pub fn get_calibration(
        &self,
        depth_mode: k4a_depth_mode_t,
        color_resolution: k4a_color_resolution_t,
    ) -> Result<Calibration, &'static str> {
        let mut calibration_handle = k4a_calibration_t::default();
        match unsafe {
            k4a_device_get_calibration(
                self.handle,
                depth_mode,
                color_resolution,
                &mut calibration_handle,
            )
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(Calibration {
                handle: calibration_handle,
            }),
            k4a_result_t::K4A_RESULT_FAILED => {
                Err("Failed to acquire calibration data for the `Device`")
            }
        }
    }

    /// Acquire raw camera calibration for the `Device`.
    ///
    /// **Return value:**
    /// * **Ok(&[u8])** containing the raw calibration data on success.
    /// * **Err(&str)** on failure.
    pub fn get_raw_calibration(&self) -> Result<&[u8], &'static str> {
        let mut calibration_data_length = 0;
        match unsafe {
            k4a_device_get_raw_calibration(
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
            k4a_device_get_raw_calibration(
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

    /// Acquire the `Device` jack status for the synchronization in connector.
    ///
    /// **Return value:**
    /// * **Ok(true)** containing the state on success.
    /// * **Err(&str)** on failure.
    pub fn is_sync_in_connected(&self) -> Result<bool, &'static str> {
        let mut sync_in_jack_connected = false;
        match unsafe {
            k4a_device_get_sync_jack(self.handle, &mut sync_in_jack_connected, &mut false)
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(sync_in_jack_connected),
            k4a_result_t::K4A_RESULT_FAILED => {
                Err("Failed to determine the status for the synchronization in connector")
            }
        }
    }

    /// Acquire the `Device` jack status for the synchronization out connector.
    ///
    /// **Return value:**
    /// * **Ok(true)** containing the state on success.
    /// * **Err(&str)** on failure.
    pub fn is_sync_out_connected(&self) -> Result<bool, &'static str> {
        let mut sync_out_jack_connected = false;
        match unsafe {
            k4a_device_get_sync_jack(self.handle, &mut false, &mut sync_out_jack_connected)
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(sync_out_jack_connected),
            k4a_result_t::K4A_RESULT_FAILED => {
                Err("Failed to determine the status for the synchronization out connector")
            }
        }
    }

    /// Determine the versions of the `Device` subsystems.
    ///
    /// **Return value:**
    /// * **Ok(k4a_hardware_version_t)** on success.
    /// * **Err(&str)** on failure.
    pub fn get_version(&self) -> Result<k4a_hardware_version_t, &'static str> {
        let mut version = k4a_hardware_version_t::default();
        match unsafe { k4a_device_get_version(self.handle, &mut version) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(version),
            k4a_result_t::K4A_RESULT_FAILED => {
                Err("Failed to determine the version of the `Device`")
            }
        }
    }
}
