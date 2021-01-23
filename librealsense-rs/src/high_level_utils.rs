// License: MIT. See LICENSE file in root directory.
// Copyright(c) 2019 Aivero. All Rights Reserved.
use crate::config::Config;
use crate::context::Context;
use crate::error::Error;
use crate::pipeline::Pipeline;
use crate::pipeline_profile::PipelineProfile;
use crate::stream_profile::{StreamData, StreamResolution};
use rs2::rs2_camera_info::*;

/// Print to STDOUT what RealSense [`Device`](../device/struct.Device.html)s are connected.
///
/// # Returns
/// * `Ok()` on success.
/// * `Err(Error)` on failure.
pub fn list_connected_devices() -> Result<(), Error> {
    let context = Context::new()?;
    let devices = context.query_devices()?;
    let device_count = devices.len();
    println!("-------------------------");
    if device_count == 0 {
        println!("No RealSense device is connected.");
    } else {
        println!(
            "The following {} RealSense devices are connected:",
            device_count
        );
        for device in devices.iter() {
            let name = device.get_info(RS2_CAMERA_INFO_NAME)?;
            let serial = device.get_info(RS2_CAMERA_INFO_SERIAL_NUMBER)?;
            let version = device.get_info(RS2_CAMERA_INFO_FIRMWARE_VERSION)?;
            let port = device.get_info(RS2_CAMERA_INFO_PHYSICAL_PORT)?;
            println!(
                "{}\tport:{}\tserial:{}\tversion:{}",
                name, port, serial, version
            );
        }
    }
    println!("-------------------------");
    Ok(())
}

/// Start a connected [`Device`](../device/struct.Device.html) with the corresponding
/// [`Config`](../config/struct.Config.html) and `index`.
///
/// # Arguments
/// * `config` - A [`Config`](../config/struct.Config.html) with
/// requested filters on the [`Pipeline`](../pipeline/struct.Pipeline.html) configuration.
/// * `index` - An index of the [`Device`](../device/struct.Device.html). Set to 0 to enable first
/// connected device.
///
/// # Returns
/// * `Ok(Pipeline)` on success.
/// * `Err(Error)` on failure.
pub fn start_device_with_index(config: &mut Config, index: usize) -> Result<Pipeline, Error> {
    let context = Context::new()?;
    let devices = context.query_devices()?;
    let device_count = devices.len();
    if index + 1 > device_count {
        Err(Error::default())
    } else {
        let serial = devices[index].get_info(RS2_CAMERA_INFO_SERIAL_NUMBER)?;
        config.enable_device(&serial)?;
        let pipeline = Pipeline::new(&context)?;
        pipeline.start_with_config(config)?;
        Ok(pipeline)
    }
}

/// Helper struct for `get_info_all_streams()`.
pub struct StreamInfo {
    pub data: StreamData,
    pub resolution: StreamResolution,
}
/// Retrieve information about all enabled streams based on a running
/// [`Pipeline`](../pipeline/struct.Pipeline.html).
///
/// # Arguments
/// * pipeline_profile - The [`PipelineProfile`](../pipeline_profile/struct.PipelineProfile.html)
/// to extract the information from.
///
/// # Returns
/// * `Ok(Vec<StreamInfo>)` on success.
/// * `Err(Error)` on failure.
pub fn get_info_all_streams(pipeline_profile: &PipelineProfile) -> Result<Vec<StreamInfo>, Error> {
    let mut info_all_streams: Vec<StreamInfo> = Vec::new();

    let streams = pipeline_profile.get_streams()?;

    for stream_profile in streams.iter() {
        let stream_data = stream_profile.get_data()?;
        let stream_resolution = stream_profile.get_resolution()?;
        info_all_streams.push(StreamInfo {
            data: stream_data,
            resolution: stream_resolution,
        })
    }

    Ok(info_all_streams)
}
