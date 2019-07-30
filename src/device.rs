use crate::error::Error;
use crate::sensor::Sensor;
use crate::util;

#[derive(Debug)]
pub struct Device {
    pub raw: *mut rs2::rs2_device,
}

impl Drop for Device {
    fn drop(&mut self) {
        unsafe {
            rs2::rs2_delete_device(self.raw);
        }
    }
}

impl Device {
    pub fn get_sensors(&self) -> Result<Vec<Sensor>, Error> {
        let mut error = Error::default();
        let sensor_list = unsafe { rs2::rs2_query_sensors(self.raw, error.inner()) };
        if error.check() {
            return Err(error);
        };

        let count = unsafe { rs2::rs2_get_sensors_count(sensor_list, error.inner()) };
        let mut res: Vec<Sensor> = Vec::new();
        for i in 0..count {
            res.push(Sensor {
                raw: unsafe { rs2::rs2_create_sensor(sensor_list, i, error.inner()) },
            });
            if error.check() {
                return Err(error);
            };
        }
        Ok(res)
    }

    // RS2_CAMERA_INFO_NAME                           , /**< Friendly name */
    // RS2_CAMERA_INFO_SERIAL_NUMBER                  , /**< Device serial number */
    // RS2_CAMERA_INFO_FIRMWARE_VERSION               , /**< Primary firmware version */
    // RS2_CAMERA_INFO_RECOMMENDED_FIRMWARE_VERSION   , /**< Recommended firmware version */
    // RS2_CAMERA_INFO_PHYSICAL_PORT                  , /**< Unique identifier of the port the device is connected to (platform specific) */
    // RS2_CAMERA_INFO_DEBUG_OP_CODE                  , /**< If device supports firmware logging, this is the command to send to get logs from firmware */
    // RS2_CAMERA_INFO_ADVANCED_MODE                  , /**< True iff the device is in advanced mode */
    // RS2_CAMERA_INFO_PRODUCT_ID                     , /**< Product ID as reported in the USB descriptor */
    // RS2_CAMERA_INFO_CAMERA_LOCKED                  , /**< True iff EEPROM is locked */
    // RS2_CAMERA_INFO_USB_TYPE_DESCRIPTOR            , /**< Designated USB specification: USB2/USB3 */
    // RS2_CAMERA_INFO_PRODUCT_LINE                   , /**< Device product line D400/SR300/L500/T200 */
    // RS2_CAMERA_INFO_ASIC_SERIAL_NUMBER             , /**< ASIC serial number */
    // RS2_CAMERA_INFO_COUNT                            /**< Number of enumeration values. Not a valid input: intended to be used in for-loops. */
    pub fn get_info(&self, info_field: rs2::rs2_camera_info) -> Result<String, Error> {
        let mut error = Error::default();
        let ret;
        unsafe {
            ret = rs2::rs2_get_device_info(self.raw, info_field, error.inner());
        }

        if error.check() {
            Err(Error::new("Failed to get device info"))
        } else {
            Ok(util::to_string(ret))
        }
    }

    pub fn hardware_reset(&self) -> Result<(), Error> {
        let mut error = Error::default();
        unsafe {
            rs2::rs2_hardware_reset(self.raw, error.inner());
        }

        if error.check() {
            Err(Error::new("Failed to reset device"))
        } else {
            Ok(())
        }
    }

    pub fn is_advanced_mode_enabled(&self) -> Result<bool, Error> {
        let mut error = Error::default();
        let is_enabled: &mut i32 = &mut (-1);
        unsafe {
            rs2::rs2_is_enabled(self.raw, is_enabled as *mut i32, error.inner());
        }
        if error.check() {
            Err(Error::new(
                "Failed to get the current state of advanced mode",
            ))
        } else {
            if *is_enabled == 1 {
                Ok(true)
            } else {
                Ok(false)
            }
        }
    }

    pub fn set_advanced_mode(&self, enable: bool) -> Result<(), Error> {
        let mut error = Error::default();
        if enable == true {
            unsafe {
                rs2::rs2_toggle_advanced_mode(self.raw, 1, error.inner());
            };
        } else {
            unsafe {
                rs2::rs2_toggle_advanced_mode(self.raw, 0, error.inner());
            };
        }

        if error.check() {
            Err(Error::new("Failed to set advanced mode"))
        } else {
            Ok(())
        }
    }

    pub fn load_json(&self, json_content: String) -> Result<(), Error> {
        let mut error = Error::default();

        unsafe {
            rs2::rs2_load_json(
                self.raw,
                Box::into_raw(json_content.to_owned().into_boxed_str().into_boxed_bytes())
                    as *const std::os::raw::c_void,
                json_content.len() as u32,
                error.inner(),
            );
        };

        if error.check() {
            Err(Error::new("Failed to load json"))
        } else {
            Ok(())
        }
    }
}
