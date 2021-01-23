// License: MIT. See LICENSE file in root directory.
// Copyright(c) 2019 Aivero. All Rights Reserved.

use std::collections::HashMap;

pub enum MetadataAttribute {
    FrameCounter = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_FRAME_COUNTER as isize,
    FrameTimestamp = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_FRAME_TIMESTAMP as isize,
    SensorTimestamp = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_SENSOR_TIMESTAMP as isize,
    ActualExposure = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_ACTUAL_EXPOSURE as isize,
    GainLevel = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_GAIN_LEVEL as isize,
    AutoExposure = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_AUTO_EXPOSURE as isize,
    WhiteBalance = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_WHITE_BALANCE as isize,
    TimeOfArrival = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_TIME_OF_ARRIVAL as isize,
    Temperature = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_TEMPERATURE as isize,
    BackendTimestamp = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_BACKEND_TIMESTAMP as isize,
    ActualFPS = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_ACTUAL_FPS as isize,
    LaserPower = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_FRAME_LASER_POWER as isize,
    LaserPowerMode =
        rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_FRAME_LASER_POWER_MODE as isize,
    ExposurePriority = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_EXPOSURE_PRIORITY as isize,
    ExposureRoiLeft = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_EXPOSURE_ROI_LEFT as isize,
    ExposureRoiRight = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_EXPOSURE_ROI_RIGHT as isize,
    ExposureRoiTop = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_EXPOSURE_ROI_TOP as isize,
    ExposureRoiBottom =
        rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_EXPOSURE_ROI_BOTTOM as isize,
    Brightness = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_BRIGHTNESS as isize,
    Contrast = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_CONTRAST as isize,
    Saturation = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_SATURATION as isize,
    Sharpness = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_SHARPNESS as isize,
    WhiteBalanceTemperature =
        rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_AUTO_WHITE_BALANCE_TEMPERATURE as isize,
    BacklightCompensation =
        rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_BACKLIGHT_COMPENSATION as isize,
    Hue = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_HUE as isize,
    Gamma = rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_GAMMA as isize,
    ManualWhiteBalance =
        rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_MANUAL_WHITE_BALANCE as isize,
    PowerLineFrequency =
        rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_POWER_LINE_FREQUENCY as isize,
    LowLightCompensation =
        rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_LOW_LIGHT_COMPENSATION as isize,
}

#[derive(Debug)]
pub struct Metadata {
    pub frame_counter: Option<i64>,
    pub frame_timestamp: Option<i64>,
    pub sensor_timestamp: Option<i64>,
    pub actual_exposure: Option<i64>,
    pub gain_level: Option<i64>,
    pub auto_exposure: Option<i64>,
    pub white_balance: Option<i64>,
    pub time_of_arrival: Option<i64>,
    pub temperature: Option<i64>,
    pub backend_timestamp: Option<i64>,
    pub actual_fps: Option<i64>,
    pub laser_power: Option<i64>,
    pub laser_power_mode: Option<i64>,
    pub exposure_priority: Option<i64>,
    pub exposure_roi_left: Option<i64>,
    pub exposure_roi_right: Option<i64>,
    pub exposure_roi_top: Option<i64>,
    pub exposure_roi_bottom: Option<i64>,
    pub brightness: Option<i64>,
    pub contrast: Option<i64>,
    pub saturation: Option<i64>,
    pub sharpness: Option<i64>,
    pub auto_white_balance_temperature: Option<i64>,
    pub backlight_compensation: Option<i64>,
    pub hue: Option<i64>,
    pub gamma: Option<i64>,
    pub manual_white_balance: Option<i64>,
    pub power_line_frequency: Option<i64>,
    pub low_light_compensation: Option<i64>,
}

impl Default for Metadata {
    fn default() -> Self {
        Self {
            frame_counter: None,
            frame_timestamp: None,
            sensor_timestamp: None,
            actual_exposure: None,
            gain_level: None,
            auto_exposure: None,
            white_balance: None,
            time_of_arrival: None,
            temperature: None,
            backend_timestamp: None,
            actual_fps: None,
            laser_power: None,
            laser_power_mode: None,
            exposure_priority: None,
            exposure_roi_left: None,
            exposure_roi_right: None,
            exposure_roi_top: None,
            exposure_roi_bottom: None,
            brightness: None,
            contrast: None,
            saturation: None,
            sharpness: None,
            auto_white_balance_temperature: None,
            backlight_compensation: None,
            hue: None,
            gamma: None,
            manual_white_balance: None,
            power_line_frequency: None,
            low_light_compensation: None,
        }
    }
}

impl Metadata {
    pub(crate) fn from(values: HashMap<u32, i64>) -> Metadata {
        let mut md = Metadata::default();

        for (field_idnf, value) in values.iter() {
            match *field_idnf {
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_FRAME_COUNTER => {
                    md.frame_counter = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_FRAME_TIMESTAMP => {
                    md.frame_timestamp = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_SENSOR_TIMESTAMP => {
                    md.sensor_timestamp = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_ACTUAL_EXPOSURE => {
                    md.actual_exposure = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_GAIN_LEVEL => {
                    md.gain_level = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_AUTO_EXPOSURE => {
                    md.auto_exposure = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_WHITE_BALANCE => {
                    md.white_balance = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_TIME_OF_ARRIVAL => {
                    md.time_of_arrival = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_TEMPERATURE => {
                    md.temperature = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_BACKEND_TIMESTAMP => {
                    md.backend_timestamp = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_ACTUAL_FPS => {
                    md.actual_fps = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_FRAME_LASER_POWER => {
                    md.laser_power = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_FRAME_LASER_POWER_MODE => {
                    md.laser_power_mode = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_EXPOSURE_PRIORITY => {
                    md.exposure_priority = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_EXPOSURE_ROI_LEFT => {
                    md.exposure_roi_left = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_EXPOSURE_ROI_RIGHT => {
                    md.exposure_roi_right = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_EXPOSURE_ROI_TOP => {
                    md.exposure_roi_top = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_EXPOSURE_ROI_BOTTOM => {
                    md.exposure_roi_bottom = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_BRIGHTNESS => {
                    md.brightness = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_CONTRAST => {
                    md.contrast = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_SATURATION => {
                    md.saturation = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_SHARPNESS => {
                    md.sharpness = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_AUTO_WHITE_BALANCE_TEMPERATURE => {
                    md.auto_white_balance_temperature = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_BACKLIGHT_COMPENSATION => {
                    md.backlight_compensation = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_HUE => {
                    md.hue = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_GAMMA => {
                    md.gamma = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_MANUAL_WHITE_BALANCE => {
                    md.manual_white_balance = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_POWER_LINE_FREQUENCY => {
                    md.power_line_frequency = Some(*value);
                }
                rs2::rs2_frame_metadata_value_RS2_FRAME_METADATA_LOW_LIGHT_COMPENSATION => {
                    md.low_light_compensation = Some(*value);
                }
                _ => unreachable!("An invalid RealSense metadata_value was found!"),
            }
        }
        md
    }
}
