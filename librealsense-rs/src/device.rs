// License: MIT. See LICENSE file in root directory.
// Copyright(c) 2019 Aivero. All Rights Reserved.
use crate::error::Error;
use crate::low_level_utils::cstring_to_string;
use crate::sensor::Sensor;

// Expose `rs2_camera_info` for external use.
pub use rs2::rs2_camera_info;

pub struct DeviceList {
    pub(crate) handle: *mut rs2::rs2_device_list,
}

impl Drop for DeviceList {
    fn drop(&mut self) {
        unsafe {
            rs2::rs2_delete_device_list(self.handle);
        }
    }
}

/// Struct representation of a [`Device`](../device/struct.Device.html) that wraps
/// around `rs2_device` handle, which exposes the functionality of RealSense devices.
pub struct Device {
    pub(crate) handle: *mut rs2::rs2_device,
}

/// Safe releasing of the `rs2_device` handle.
impl Drop for Device {
    fn drop(&mut self) {
        unsafe {
            rs2::rs2_delete_device(self.handle);
        }
    }
}

unsafe impl Send for Device {}
unsafe impl Sync for Device {}

impl Device {
    /// Create a static snapshot of all connected
    /// [`Sensor`](../sensor/struct.Sensor.html)s within a specific
    /// [`Device`](../device/struct.Device.html).
    ///
    /// # Returns
    /// * `Ok(Vec<Sensor>)` on success.
    /// * `Err(Error)` on failure.
    pub fn query_sensors(&self) -> Result<Vec<Sensor>, Error> {
        let mut error = Error::default();
        let sensor_list = unsafe { rs2::rs2_query_sensors(self.handle, error.inner()) };
        if error.check() {
            return Err(error);
        };
        let sensor_count = unsafe { rs2::rs2_get_sensors_count(sensor_list, error.inner()) };
        let mut sensors: Vec<Sensor> = Vec::new();
        for sensor_index in 0..sensor_count {
            sensors.push(Sensor {
                handle: unsafe { rs2::rs2_create_sensor(sensor_list, sensor_index, error.inner()) },
            });
            if error.check() {
                return Err(error);
            };
        }
        Ok(sensors)
    }

    #[deprecated(
        since = "0.6.0",
        note = "Use `query_sensors()` to be consistent with C/C++ API"
    )]
    pub fn get_sensors(&self) -> Result<Vec<Sensor>, Error> {
        self.query_sensors()
    }

    /// Check if a specific camera `info` is supported by the
    /// [`Device`](../device/struct.Device.html).
    ///
    /// # Arguments
    /// * `info` - The parameter to check for support.
    ///
    /// # Returns
    /// * `Ok(bool)` on success.
    /// * `Err(Error)` on failure.
    pub fn supports_info(&self, _info: rs2_camera_info) -> Result<bool, Error> {
        unimplemented!()
    }

    /// Retrieve camera specific information, like versions of various internal components.
    ///
    /// # Arguments
    /// * `info` - The camera info type to retrieve. Please see
    /// [rs2_camera_info](../device/enum.rs2_camera_info.html) for more information.
    ///
    /// # Returns
    /// * `Ok(String)` on success, containing the value under the info field.
    /// * `Err(Error)` on failure.
    pub fn get_info(&self, info: rs2_camera_info) -> Result<String, Error> {
        let mut error = Error::default();
        let ret = unsafe { rs2::rs2_get_device_info(self.handle, info, error.inner()) };
        if error.check() {
            Err(error)
        } else {
            Ok(cstring_to_string(ret))
        }
    }

    /// Send hardware reset request to the [`Device`](../device/struct.Device.html).
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(Error)` on failure.
    pub fn hardware_reset(&self) -> Result<(), Error> {
        let mut error = Error::default();
        unsafe {
            rs2::rs2_hardware_reset(self.handle, error.inner());
        }
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    /// Update [`Device`](../device/struct.Device.html) to the provided firmware, the
    /// device must be extendable to `RS2_EXTENSION_UPDATABLE`. This call is executed on the
    /// caller's thread and it supports progress notifications via the optional callback.
    ///
    /// # Arguments
    /// * `info` - The parameter to check for support.
    /// * `fw_image` - Firmware image buffer.
    /// * `fw_image_size` - Firmware image buffer size.
    /// * `callback` - Optional callback for update progress notifications, the progress value is
    /// normailzed to 1.
    /// * `client_data` - Optional client data for the callback.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(Error)` on failure.
    pub fn update_firmware(&self) -> Result<(), Error> {
        unimplemented!();
    }

    /// Send hardware reset request to the [`Device`](../device/struct.Device.html).
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(Error)` on failure.
    pub fn is_advanced_mode_enabled(&self) -> Result<bool, Error> {
        let mut error = Error::default();
        let is_enabled: &mut i32 = &mut (-1);
        unsafe {
            rs2::rs2_is_enabled(self.handle, is_enabled as *mut i32, error.inner());
        }
        if error.check() {
            Err(error)
        } else if *is_enabled == 1 {
            Ok(true)
        } else {
            Ok(false)
        }
    }

    /// Enable or disable advanced mode for a [`Device`](../device/struct.Device.html).
    ///
    /// # Arguments
    /// * `enable` - The desired state of advanced mode after callback.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(Error)` on failure.
    pub fn set_advanced_mode(&self, enable: bool) -> Result<(), Error> {
        let mut error = Error::default();
        if enable {
            unsafe {
                rs2::rs2_toggle_advanced_mode(self.handle, 1, error.inner());
            };
        } else {
            unsafe {
                rs2::rs2_toggle_advanced_mode(self.handle, 0, error.inner());
            };
        }

        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    /// Configure device with JSON.
    ///
    /// # Arguments
    /// * `json_content` - The content of the JSON configuration.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(Error)` on failure.
    pub fn load_json(&self, json_content: &str) -> Result<(), Error> {
        let mut error = Error::default();

        unsafe {
            rs2::rs2_load_json(
                self.handle,
                Box::into_raw(json_content.to_owned().into_boxed_str().into_boxed_bytes())
                    as *const std::os::raw::c_void,
                json_content.len() as u32,
                error.inner(),
            );
        };

        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    /// Configure [`Device`](../device/struct.Device.html) with JSON file specified by
    /// `json_path`.
    ///
    /// # Arguments
    /// * `json_path` - The absolute path to JSON file.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(Error)` on failure.
    pub fn load_json_file_path(&self, json_path: &str) -> Result<(), Error> {
        if !self.is_advanced_mode_enabled()? {
            self.set_advanced_mode(true)?;
        }
        let json_content = std::fs::read_to_string(json_path).map_err(|err| {
            Error::new(
                &format!(
                    "Cannot read RealSense JSON configuration from file \"{}\" - {}",
                    json_path, err
                ),
                "Device::load_json_file_path()",
                "json_path",
                0,
            )
        })?;
        self.load_json(&json_content)?;
        Ok(())
    }
}
