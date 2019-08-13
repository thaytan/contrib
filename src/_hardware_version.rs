#![allow(non_camel_case_types)]

use crate::generated_bindings::*;

type k4a_hardware_version = k4a_hardware_version_t;
impl Default for k4a_hardware_version {
    fn default() -> Self {
        k4a_hardware_version {
            rgb: k4a_version_t::default(),
            depth: k4a_version_t::default(),
            audio: k4a_version_t::default(),
            depth_sensor: k4a_version_t::default(),
            firmware_build: k4a_firmware_build_t::K4A_FIRMWARE_BUILD_RELEASE,
            firmware_signature: k4a_firmware_signature_t::K4A_FIRMWARE_SIGNATURE_MSFT,
        }
    }
}

type k4a_version = k4a_version_t;
impl Default for k4a_version {
    fn default() -> Self {
        k4a_version {
            major: 0,
            minor: 0,
            iteration: 0,
        }
    }
}
