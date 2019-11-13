#![allow(non_camel_case_types)]

use crate::generated_bindings::*;

pub type k4a_imu_sample = k4a_imu_sample_t;
impl Default for k4a_imu_sample {
    fn default() -> Self {
        k4a_imu_sample {
            temperature: 0.0,
            acc_sample: k4a_float3_t { v: [0.0; 3] },
            acc_timestamp_usec: 0,
            gyro_sample: k4a_float3_t { v: [0.0; 3] },
            gyro_timestamp_usec: 0,
        }
    }
}
