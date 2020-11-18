use k4a_sys::*;

use crate::calibration::Calibration;
use crate::capture::Capture;
use crate::error::{K4aError, Result};
use crate::imu_sample::ImuSample;
use std::convert::TryInto;

/// Struct representation of a single
/// [*Azure Kinect DK (K4A)*](https://azure.microsoft.com/en-in/services/kinect-dk/)
/// [`Device`](../device/struct.Device.html) that wraps around `k4a_device_t`.
pub struct Device {
    pub(crate) handle: k4a_device_t,
}

/// Required for moving between threads
unsafe impl Send for Device {}
unsafe impl Sync for Device {}

/// Safe releasing of the `k4a_device_t` handle.
impl Drop for Device {
    fn drop(&mut self) {
        unsafe {
            k4a_device_close(self.handle);
        }
    }
}

impl Device {
    /// Determine number of connected [`Device`](../device/struct.Device.html)s.
    ///
    /// # Returns
    /// * Number of connected devices (`u32`) on success.
    /// * `Err(K4aError::Failure)` if no
    /// [`Device`](../device/struct.Device.html) is connected.
    pub fn get_number_of_connected_devices() -> Result<u32> {
        let device_count = unsafe { k4a_device_get_installed_count() };
        if device_count == 0 {
            Err(K4aError::Failure("No `Device` detected"))
        } else {
            Ok(device_count)
        }
    }

    /// Open a [`Device`](../device/struct.Device.html).
    ///
    /// # Arguments
    /// * `index` - Index of the device. Pass `0_u32` if only one
    /// [`Device`](../device/struct.Device.html) is connected.
    ///
    /// # Returns
    /// * `Ok(Device)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn open(index: u32) -> Result<Device> {
        let device_count = Self::get_number_of_connected_devices()?;
        if !(index < device_count) {
            return Err(K4aError::Failure(
                "`Device` with the given index is not connected",
            ));
        }

        let mut device = Device {
            handle: std::ptr::null_mut(),
        };
        match unsafe { k4a_device_open(index, &mut device.handle) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(device),
            k4a_result_t::K4A_RESULT_FAILED => {
                Err(K4aError::Failure("`Device` could not be opened"))
            }
        }
    }

    /// Acquire serial number of a [`Device`](../device/struct.Device.html).
    ///
    /// # Returns
    /// * `Ok(String)` containing the serial number on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_serial_number(&self) -> Result<String> {
        let mut serial_number_length: u64 = 0;
        match unsafe {
            k4a_device_get_serialnum(self.handle, std::ptr::null_mut(), &mut serial_number_length)
        } {
            k4a_buffer_result_t::K4A_BUFFER_RESULT_TOO_SMALL => {}
            _ => {
                return Err(K4aError::Failure(
                    "Failed to acquire the length of serial number for `Device`",
                ))
            }
        }

        let mut serial_number = vec![0_u8; serial_number_length.try_into().unwrap()];
        match unsafe {
            k4a_device_get_serialnum(
                self.handle,
                serial_number.as_mut_ptr() as *mut std::os::raw::c_char,
                &mut serial_number_length,
            )
        } {
            k4a_buffer_result_t::K4A_BUFFER_RESULT_SUCCEEDED => {
                // Pop null character (Cstring terminator)
                serial_number.pop();
                Ok(unsafe { String::from_utf8_unchecked(serial_number) })
            }
            _ => Err(K4aError::Failure(
                "Failed to acquire serial number for `Device`",
            )),
        }
    }

    /// Acquire serial number of each connected [`Device`](../device/struct.Device.html).
    ///
    /// # Returns
    /// * `Ok(<Vec<String>)` containing all serial numbers on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_connected_serial_numbers() -> Result<Vec<String>> {
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

    /// Open a [`Device`](../device/struct.Device.html) with the corresponding serial number.
    ///
    /// # Arguments
    /// * `serial` - Serial number of the [`Device`](../device/struct.Device.html).
    ///
    /// # Returns
    /// * `Ok(Device)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn open_with_serial(serial: &String) -> Result<Device> {
        for index in 0..Self::get_number_of_connected_devices()? {
            if let Ok(device) = Device::open(index) {
                if &device.get_serial_number()? == serial {
                    return Ok(device);
                }
            }
        }
        Err(K4aError::Failure(
            "`Device` with given serial is not detected",
        ))
    }

    /// Open the first unused [`Device`](../device/struct.Device.html) that is connected to the system.
    ///
    /// # Returns
    /// * `Ok(Device)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn open_first_unused() -> Result<Device> {
        for index in 0..Self::get_number_of_connected_devices()? {
            let device = Device::open(index);
            if device.is_ok() {
                return device;
            }
        }
        Err(K4aError::Failure("No unused `Device` is connected"))
    }

    /// Start cameras of a [`Device`](../device/struct.Device.html).
    ///
    /// # Arguments
    /// * `configuration` - [`Device`](../device/struct.Device.html) configuration parameters for
    /// the cameras.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn start_cameras(&self, configuration: &DeviceConfiguration) -> Result<()> {
        match unsafe { k4a_device_start_cameras(self.handle, configuration) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(()),
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "Cameras of `Device` could not be started",
            )),
        }
    }

    /// Stop the cameras of [`Device`](../device/struct.Device.html).
    pub fn stop_cameras(&self) {
        unsafe { k4a_device_stop_cameras(self.handle) }
    }

    /// Receive a [`Capture`](../capture/struct.Capture.html) from a
    /// [`Device`](../device/struct.Device.html).
    ///
    /// # Arguments
    /// * `timeout` - Timeout in milliseconds.
    ///
    /// # Returns
    /// * `Ok(Capture)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    /// * `Err(K4aError::Timeout)` on timeout.
    pub fn get_capture(&self, timeout: i32) -> Result<Capture> {
        let mut capture = Capture {
            handle: std::ptr::null_mut(),
        };
        match unsafe { k4a_device_get_capture(self.handle, &mut capture.handle, timeout) } {
            k4a_wait_result_t::K4A_WAIT_RESULT_SUCCEEDED => Ok(capture),
            k4a_wait_result_t::K4A_WAIT_RESULT_TIMEOUT => Err(K4aError::Timeout),
            k4a_wait_result_t::K4A_WAIT_RESULT_FAILED => {
                Err(K4aError::Failure("`Capture` could not be obtained"))
            }
        }
    }

    /// Start IMU of a [`Device`](../device/struct.Device.html).
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn start_imu(&self) -> Result<()> {
        match unsafe { k4a_device_start_imu(self.handle) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(()),
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure("IMU could not be started")),
        }
    }

    /// Stop IMU of [`Device`](../device/struct.Device.html).
    pub fn stop_imu(&self) {
        unsafe { k4a_device_stop_imu(self.handle) }
    }

    /// Receive an [`ImuSample`](../imu_sample/struct.ImuSample.html) from a
    /// [`Device`](../device/struct.Device.html).
    ///
    /// Note that IMU samples are generated at a higher frequency than images, so it is possible
    /// to acquire more samples from queue in between two
    /// [`Capture`](../capture/struct.Capture.html)s.
    ///
    /// # Arguments
    /// * `timeout` - Timeout in milliseconds. To retrieve all the currently queued samples, call
    /// the function with `timeout` of 0 in a loop until the function returns
    /// `Err(K4aError::Failure)`.
    ///
    /// # Returns
    /// * `Ok(ImuSample)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    /// * `Err(K4aError::Timeout)` on timeout.
    pub fn get_imu_sample(&self, timeout: i32) -> Result<ImuSample> {
        let mut imu_sample_handle = k4a_imu_sample_t::default();
        match unsafe { k4a_device_get_imu_sample(self.handle, &mut imu_sample_handle, timeout) } {
            k4a_wait_result_t::K4A_WAIT_RESULT_SUCCEEDED => Ok(ImuSample {
                handle: imu_sample_handle,
            }),
            k4a_wait_result_t::K4A_WAIT_RESULT_TIMEOUT => Err(K4aError::Timeout),
            k4a_wait_result_t::K4A_WAIT_RESULT_FAILED => {
                Err(K4aError::Failure("`ImuSample` could not be obtained"))
            }
        }
    }

    /// Retrieve mode of color control `command` and value of mode is set to
    /// `K4A_COLOR_CONTROL_MODE_MANUAL`.
    ///
    /// # Arguments
    /// * `command` - Field to read from.
    ///
    /// # Returns
    /// * `Ok(Some(i32))` on success. It contains the `command` value if mode is set to
    /// `K4A_COLOR_CONTROL_MODE_MANUAL`.
    /// * `Ok(None)` on success if mode is set to `K4A_COLOR_CONTROL_MODE_AUTO`.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_color_control(&self, command: ColorControlCommand) -> Result<Option<i32>> {
        let mut mode = k4a_color_control_mode_t::K4A_COLOR_CONTROL_MODE_AUTO;
        let mut value: i32 = 0;
        match unsafe { k4a_device_get_color_control(self.handle, command, &mut mode, &mut value) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(match mode {
                k4a_color_control_mode_t::K4A_COLOR_CONTROL_MODE_AUTO => None,
                k4a_color_control_mode_t::K4A_COLOR_CONTROL_MODE_MANUAL => Some(value),
            }),
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to acquire color sensor control value",
            )),
        }
    }

    /// This function is NOT implemented!
    pub fn get_color_control_capabilities(&self) {
        unimplemented!()
    }

    /// Set `command` to `K4A_COLOR_CONTROL_MODE_MANUAL` mode with the specified `value`.
    ///
    /// # Arguments
    /// * `command` - Field to modify.
    /// * `value` - Value to set the `command` to.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn set_color_control_manual(&self, command: ColorControlCommand, value: i32) -> Result<()> {
        match unsafe {
            k4a_device_get_color_control(
                self.handle,
                command,
                &mut k4a_color_control_mode_t::K4A_COLOR_CONTROL_MODE_MANUAL,
                &mut value.clone(),
            )
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(()),
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to set color sensor control command to manual mode with a specified value",
            )),
        }
    }

    /// Set `command` to `K4A_COLOR_CONTROL_MODE_AUTO` mode.
    ///
    /// # Arguments
    /// * `command` - Field to modify.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn set_color_control_auto(&self, command: ColorControlCommand) -> Result<()> {
        match unsafe {
            k4a_device_get_color_control(
                self.handle,
                command,
                &mut k4a_color_control_mode_t::K4A_COLOR_CONTROL_MODE_AUTO,
                &mut 0,
            )
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(()),
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to set color sensor control command to automatic mode",
            )),
        }
    }

    /// Acquire [`Calibration`](../calibration/struct.Calibration.html) for the
    /// [`Device`](../device/struct.Device.html).
    ///
    /// # Arguments
    /// * `depth_mode` - Mode of the depth camera.
    /// * `color_resolution` - Resolution of the color camera.
    ///
    /// # Returns
    /// * `Ok(Calibration)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_calibration(
        &self,
        depth_mode: DepthMode,
        color_resolution: ColorResolution,
    ) -> Result<Calibration> {
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
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to acquire `Calibration` for the `Device`",
            )),
        }
    }

    /// Acquire raw camera calibration for the [`Device`](../device/struct.Device.html).
    ///
    /// # Returns
    /// * `Ok(&[u8])` containing the raw calibration data on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_raw_calibration(&self) -> Result<&[u8]> {
        let mut calibration_data_length: u64 = 0;
        match unsafe {
            k4a_device_get_raw_calibration(
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
            k4a_device_get_raw_calibration(
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

    /// Acquire the [`Device`](../device/struct.Device.html) jack status for the synchronization in
    /// connector.
    ///
    /// # Returns
    /// * `Ok(bool)` containing the state on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn is_sync_in_connected(&self) -> Result<bool> {
        let mut sync_in_jack_connected = false;
        match unsafe {
            k4a_device_get_sync_jack(self.handle, &mut sync_in_jack_connected, &mut false)
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(sync_in_jack_connected),
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to determine the status for the synchronization in connector",
            )),
        }
    }

    /// Acquire the [`Device`](../device/struct.Device.html) jack status for the synchronization
    /// out connector.
    ///
    /// # Returns
    /// * `Ok(bool)` containing the state on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn is_sync_out_connected(&self) -> Result<bool> {
        let mut sync_out_jack_connected = false;
        match unsafe {
            k4a_device_get_sync_jack(self.handle, &mut false, &mut sync_out_jack_connected)
        } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(sync_out_jack_connected),
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to determine the status for the synchronization out connector",
            )),
        }
    }

    /// Determine the versions of the [`Device`](../device/struct.Device.html) subsystems.
    ///
    /// # Returns
    /// * `Ok(HardwareVersion)` on success.
    /// * `Err(K4aError::Failure)` on failure.
    pub fn get_version(&self) -> Result<HardwareVersion> {
        let mut version = HardwareVersion::default();
        match unsafe { k4a_device_get_version(self.handle, &mut version) } {
            k4a_result_t::K4A_RESULT_SUCCEEDED => Ok(version),
            k4a_result_t::K4A_RESULT_FAILED => Err(K4aError::Failure(
                "Failed to determine the version of the `Device`",
            )),
        }
    }
}
