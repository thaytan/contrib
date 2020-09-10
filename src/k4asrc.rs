// Aivero
// Copyright (C) <2019> Aivero
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Library General Public
// License as published by the Free Software Foundation; either
// version 2 of the License, or (at your option) any later version.
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Library General Public License for more details.
// You should have received a copy of the GNU Library General Public
// License along with this library; if not, write to the
// Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
// Boston, MA 02110-1301, USA.

use crate::enums::*;
use crate::error::*;
use crate::properties::*;
use crate::settings::*;
use crate::stream_properties::*;
use crate::streams::*;
use crate::timestamp_source::*;
use crate::utilities::*;
use ::rgbd_timestamps::*;
use camera_meta::Distortion;
use glib::subclass;
use gst::subclass::prelude::*;
use gst_base::prelude::*;
use gst_base::subclass::base_src::CreateSuccess;
use gst_base::subclass::prelude::*;
use gst_depth_meta::{camera_meta, camera_meta::*, rgbd};
use k4a::calibration::Calibration;
use k4a::camera_calibration::CameraCalibration;
use k4a::capture::Capture;
use k4a::device::Device;
use k4a::error::K4aError;
use k4a::imu_sample::ImuSample;
use k4a::playback::Playback;
use k4a::transformation::Transformation;
use k4a::CalibrationType::*;
use k4a::*;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

/// A struct representation of the `k4asrc` element.
struct K4aSrc {
    /// Internals of `k4asrc` element that are locked under mutex.
    internals: Mutex<K4aSrcInternals>,
    /// Contains timestamp internals utilised by `RgbdTimestamps` trait.
    timestamp_internals: Arc<Mutex<TimestampInternals>>,
}

lazy_static! {
    /// Debug category of `k4asrc` element.
    static ref CAT: gst::DebugCategory = gst::DebugCategory::new(
        "k4asrc",
        gst::DebugColorFlags::empty(),
        Some("K4A Source"),
);
}

/// Internals of the element that are under a mutex.
struct K4aSrcInternals {
    /// Reconfigurable properties.
    settings: Settings,
    /// Contains information about the utilised K4A source.
    stream_source: Option<StreamSource>,
    /// Contains calibration data specific to the Device or Playback the is utilised for streaming.
    camera: CameraInternals,
}

/// An enum that contains information about stream source from either playback and physical K4A device.
enum StreamSource {
    /// Variant that contains information about playback stream source.
    Playback(Playback, RecordConfiguration),
    /// Variant that contains information about device stream source.
    Device(Device, DeviceConfiguration),
}

/// A Struct that contains calibration data specific to the Device or Playback the is utilised for streaming.
struct CameraInternals {
    /// Contains transformation used during rectification. Valid only if `rectify-depth=true`, otherwise None.
    transformation: Option<Transformation>,
    /// Contains CameraMeta serialised with Cap'n Proto. Valid only if `attach-camera-meta=true`, otherwise empty.
    camera_meta_serialised: Vec<u8>,
}

impl ObjectSubclass for K4aSrc {
    const NAME: &'static str = "k4asrc";
    type ParentType = gst_base::BaseSrc;
    type Instance = gst::subclass::ElementInstanceStruct<Self>;
    type Class = subclass::simple::ClassStruct<Self>;

    glib_object_subclass!();

    fn class_init(klass: &mut subclass::simple::ClassStruct<Self>) {
        klass.set_metadata(
            "K4A Source",
            "Source/RGB-D/K4A",
            "Stream `video/rgbd` from an Azure Kinect DK (K4A) device",
            "Andrej Orsula <andrej.orsula@aivero.com>",
        );

        // Install properties for streaming from K4A
        klass.install_properties(PROPERTIES.as_ref());

        let allowed_framerates = K4aFramerate::allowed_framerates();

        // Create src pad template with `video/rgbd` caps
        let src_caps = gst::Caps::new_simple(
            "video/rgbd",
            &[
                // A list of the available K4A streams, indicating their respective priority
                (
                    "streams",
                    &format! {"{},{},{},{},{}", STREAM_ID_DEPTH, STREAM_ID_IR, STREAM_ID_COLOR, STREAM_ID_IMU, STREAM_ID_CAMERAMETA},
                ),
                (
                    // Framerates at which K4A is capable of providing stream
                    "framerate",
                    &gst::List::new(&[
                        &gst::Fraction::new(allowed_framerates[0], 1),
                        &gst::Fraction::new(allowed_framerates[1], 1),
                        &gst::Fraction::new(allowed_framerates[2], 1),
                    ]),
                ),
            ],
        );
        klass.add_pad_template(
            gst::PadTemplate::new(
                "src",
                gst::PadDirection::Src,
                gst::PadPresence::Always,
                &src_caps,
            )
            .expect("k4asrc: Cannot add template for src pad"),
        );
    }

    fn new() -> Self {
        Self {
            internals: Mutex::new(K4aSrcInternals {
                settings: Settings::default(),
                stream_source: None,
                camera: CameraInternals {
                    transformation: None,
                    camera_meta_serialised: Vec::default(),
                },
            }),
            timestamp_internals: Arc::new(Mutex::new(TimestampInternals::default())),
        }
    }
}

impl BaseSrcImpl for K4aSrc {
    fn start(&self, _base_src: &gst_base::BaseSrc) -> Result<(), gst::ErrorMessage> {
        // Lock the internals
        let internals = &mut *self
            .internals
            .lock()
            .expect("k4asrc: Cannot lock internals in `start()`");

        // Initiate streaming from K4A
        Self::start_k4a(internals)?;

        // Return `Ok()` if everything went fine and start streaming
        Ok(())
    }

    fn stop(&self, base_src: &gst_base::BaseSrc) -> Result<(), gst::ErrorMessage> {
        // Lock the internals
        let internals = &mut *self
            .internals
            .lock()
            .expect("k4asrc: Cannot lock internals in `start()`");

        // Stop live streaming from K4A `Device`
        match &internals.stream_source {
            Some(StreamSource::Device(device, _device_configuration)) => {
                if internals.settings.desired_streams.imu {
                    device.stop_imu();
                }
                device.stop_cameras();
            }
            Some(StreamSource::Playback(_playback, _record_configuration)) => {}
            None => unreachable!("k4asrc: Stream source is specified before reaching `stop()`"),
        }

        // Chain up parent implementation
        self.parent_stop(base_src)
    }

    fn fixate(&self, base_src: &gst_base::BaseSrc, mut caps: gst::Caps) -> gst::Caps {
        // Lock the internals
        let internals = &mut self
            .internals
            .lock()
            .expect("k4asrc: Cannot lock internals in `fixate()`");
        let desired_streams = &internals.settings.desired_streams;

        caps.truncate();
        {
            // Map caps to mutable structure
            let caps = caps
                .make_mut()
                .get_mut_structure(0)
                .expect("k4asrc: Failed to map caps to mutable structure");
            // Fixate based on stream source
            let stream_properties = Self::get_stream_properties(
                internals.stream_source.as_ref().unwrap_or_else(|| {
                    unreachable!("k4asrc: Stream source is specified before reaching `fixate()`")
                }),
            )
            .unwrap_or_else(|err_msg| {
                panic!("k4asrc: Failed to obtain stream properties - {}", err_msg)
            });

            // Create string containing selected streams with priority `depth`>`ir`>`color`>`IMU`
            // The first stream in this string is contained in the main buffer
            let mut selected_streams = String::new();

            // Add depth stream with its format, width and height into the caps, if enabled
            if desired_streams.depth {
                selected_streams.push_str(&format!("{},", STREAM_ID_DEPTH));
                caps.set(
                    &format!("{}_format", STREAM_ID_DEPTH),
                    &k4a_image_format_to_gst_video_format(DEPTH_FORMAT)
                        .unwrap()
                        .to_string(),
                );
                // If rectified, the resolution of the depth stream is identical to color stream.
                if internals.settings.rectify_depth {
                    caps.set(
                        &format!("{}_width", STREAM_ID_DEPTH),
                        &stream_properties.color_resolution.width,
                    );
                    caps.set(
                        &format!("{}_height", STREAM_ID_DEPTH),
                        &stream_properties.color_resolution.height,
                    );
                } else {
                    caps.set(
                        &format!("{}_width", STREAM_ID_DEPTH),
                        &stream_properties.depth_resolution.width,
                    );
                    caps.set(
                        &format!("{}_height", STREAM_ID_DEPTH),
                        &stream_properties.depth_resolution.height,
                    );
                }
            }
            // Add ir stream with its format, width and height into the caps, if enabled
            if desired_streams.ir {
                selected_streams.push_str(&format!("{},", STREAM_ID_IR));
                caps.set(
                    &format!("{}_format", STREAM_ID_IR),
                    &k4a_image_format_to_gst_video_format(IR_FORMAT)
                        .unwrap()
                        .to_string(),
                );
                caps.set(
                    &format!("{}_width", STREAM_ID_IR),
                    &stream_properties.ir_resolution.width,
                );
                caps.set(
                    &format!("{}_height", STREAM_ID_IR),
                    &stream_properties.ir_resolution.height,
                );
            }
            // Add color stream with its format, width and height into the caps, if enabled
            if desired_streams.color {
                selected_streams.push_str(&format!("{},", STREAM_ID_COLOR));
                caps.set(
                    &format!("{}_format", STREAM_ID_COLOR),
                    &stream_properties.color_format.to_string(),
                );
                caps.set(
                    &format!("{}_width", STREAM_ID_COLOR),
                    &stream_properties.color_resolution.width,
                );
                caps.set(
                    &format!("{}_height", STREAM_ID_COLOR),
                    &stream_properties.color_resolution.height,
                );
            }
            // Add IMU stream, if enabled
            if desired_streams.imu {
                selected_streams.push_str(&format!("{},", STREAM_ID_IMU));
                caps.fixate_field_nearest_fraction("imu_sampling_rate", IMU_SAMPLING_RATE_HZ);
            }

            // Add camerameta stream, if enabled
            if internals.settings.attach_camera_meta {
                selected_streams.push_str(&format!("{},", STREAM_ID_CAMERAMETA));
            }

            // Pop the last ',' contained in streams (not really necessary, but nice)
            selected_streams.pop();

            // Fixate the framerate
            caps.fixate_field_nearest_fraction("framerate", stream_properties.framerate);

            // Update buffer duration for `RgbdTimestamps` trait
            self.set_buffer_duration(stream_properties.framerate as f32);

            // Finally add the streams to the caps
            caps.set("streams", &selected_streams.as_str());
        }

        // Chain up parent implementation with modified caps
        self.parent_fixate(base_src, caps)
    }

    fn create(
        &self,
        base_src: &gst_base::BaseSrc,
        _offset: u64,
        _buffer: Option<&mut gst::BufferRef>,
        _length: u32,
    ) -> Result<CreateSuccess, gst::FlowError> {
        // Lock the internals
        let internals = &mut self
            .internals
            .lock()
            .expect("k4asrc: Cannot lock internals in `create()`");
        let desired_streams = internals.settings.desired_streams;

        // Create the output buffer
        let mut output_buffer = gst::buffer::Buffer::new();

        // Get capture from the stream source
        let capture = Self::get_capture(internals)?;

        // Attach `depth` frame if enabled
        if desired_streams.depth {
            let res = self.attach_frame_to_buffer(
                base_src,
                internals,
                &mut output_buffer,
                &capture,
                STREAM_ID_DEPTH,
                &[],
            );
            if res.is_err() {
                gst_warning!(
                    CAT,
                    obj: base_src,
                    "Frame could not be attached to buffer for `{}` stream",
                    STREAM_ID_DEPTH
                );
            }
        }

        // Attach `ir` frame if enabled
        if desired_streams.ir {
            let res = self.attach_frame_to_buffer(
                base_src,
                internals,
                &mut output_buffer,
                &capture,
                STREAM_ID_IR,
                &[desired_streams.depth],
            );
            if res.is_err() {
                gst_warning!(
                    CAT,
                    obj: base_src,
                    "Frame could not be attached to buffer for `{}` stream",
                    STREAM_ID_IR
                );
            }
        }

        // Attach `color` frame if enabled
        if desired_streams.color {
            let res = self.attach_frame_to_buffer(
                base_src,
                internals,
                &mut output_buffer,
                &capture,
                STREAM_ID_COLOR,
                &[desired_streams.depth, desired_streams.ir],
            );
            if res.is_err() {
                gst_warning!(
                    CAT,
                    obj: base_src,
                    "Frame could not be attached to buffer for `{}` stream",
                    STREAM_ID_COLOR
                );
            }
        }

        // Attach `IMU` samples if enabled
        if desired_streams.imu {
            let imu_samples = Self::get_available_imu_samples(internals)?;
            self.attach_imu_samples(base_src, &mut output_buffer, imu_samples)?;
        }

        // Attach Cap'n Proto serialised `CameraMeta` if enabled
        if internals.settings.attach_camera_meta {
            // An explicit clone of the serialised buffer is used so that CameraMeta does not need to be serialised every time.
            let camera_meta = internals.camera.camera_meta_serialised.clone();
            self.attach_camera_meta(base_src, &mut output_buffer, camera_meta)?;
        }

        Ok(CreateSuccess::NewBuffer(output_buffer))
    }

    fn is_seekable(&self, _base_src: &gst_base::BaseSrc) -> bool {
        // TODO: If desired, enable and implement seeking for streaming from `Playback`
        false
    }
}

impl K4aSrc {
    /// Start streaming from K4A and configure stream source according to settings.
    ///
    /// # Arguments
    /// * `internals` - The internals of the element that contain settings and stream source.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(K4aSrcError)` on failure.
    fn start_k4a(internals: &mut K4aSrcInternals) -> Result<(), K4aSrcError> {
        let settings = &internals.settings;

        // Make sure the user enabled at least one of the streams
        if !settings.desired_streams.is_any_video_enabled() {
            return Err(K4aSrcError::Failure(
                "k4asrc: At least one of the video streams must be enabled",
            ));
        }

        // Make sure that only one stream source is selected
        if !settings.device_settings.serial.is_empty()
            && !settings.playback_settings.recording_location.is_empty()
        {
            return Err(K4aSrcError::Failure(
                "k4asrc: Both `serial` and `recording-location` are set, please select only one stream source",
            ));
        }

        // Determine whether to stream from `Playback` or `Device`
        // If `recording-location` is not set, live stream from `Device` is assumed
        if !settings.playback_settings.recording_location.is_empty() {
            Self::start_from_playback(internals)?;
        } else {
            Self::start_from_device(internals)?;
        }

        // Return `Ok()` if everything went fine
        Ok(())
    }

    /// Start streaming from K4A `Playback`.
    ///
    /// # Arguments
    /// * `internals` - The internals of the element that contain settings and stream source.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(K4aSrcError)` on failure.
    fn start_from_playback(internals: &mut K4aSrcInternals) -> Result<(), K4aSrcError> {
        let settings = &internals.settings;

        // Open `Playback`
        let playback = Playback::open(&settings.playback_settings.recording_location)?;

        // Extract `record_configuration` from the `playback`
        let record_configuration = playback.get_record_configuration()?;

        // Extract available streams from the `record_configuration`
        let available_streams = Streams {
            depth: record_configuration.depth_track_enabled,
            ir: record_configuration.ir_track_enabled,
            color: record_configuration.color_track_enabled,
            imu: record_configuration.imu_track_enabled,
        };

        // Make sure there are no conflicts between the desired and available streams
        if !Streams::are_streams_available(settings.desired_streams, available_streams) {
            return Err(K4aSrcError::Failure(
                "k4asrc: Some of the desired stream(s) are not available in the recording for playback",
          ));
        }

        // Make sure that Playback contains color stream if depth rectification is enabled
        if settings.rectify_depth && !available_streams.color {
            return Err(K4aSrcError::Failure(
                "k4asrc: Depth frames cannot be rectified if the recording does NOT contain `color` stream. \
                Please set the property `rectify-depth` to false or use a different recording.",
          ));
        }

        // Get Calibration from the Playback
        let calibration = playback.get_calibration()?;
        // Setup camera internals based on the extracted Calibration
        Self::setup_camera_internals(internals, calibration)?;

        // Update `stream_source` to `Playback`
        internals.stream_source = Some(StreamSource::Playback(playback, record_configuration));

        // Return `Ok()` if everything went fine
        Ok(())
    }

    /// Start streaming from K4A `Device`.
    ///
    /// # Arguments
    /// * `internals` - The internals of the element that contain settings and stream source.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(K4aSrcError)` on failure.
    fn start_from_device(internals: &mut K4aSrcInternals) -> Result<(), K4aSrcError> {
        let settings = &internals.settings;

        // Make sure that color stream is enabled if depth rectification is desired
        if settings.rectify_depth && !settings.desired_streams.color {
            return Err(K4aSrcError::Failure(
                "k4asrc: Depth frames cannot be rectified if `color` stream is disabled. \
                Please set `enable-color` to true or the property `rectify-depth` to false.",
            ));
        }

        // Open a `Device`
        let device = if !settings.device_settings.serial.is_empty() {
            // Open `Device` based on its `serial` number
            Device::open_with_serial(&settings.device_settings.serial)?
        } else {
            // If no serial is specified, open the first connected `Device`
            Device::open(0)?
        };

        // Create `DeviceConfiguration` based on settings
        let device_configuration = DeviceConfiguration::try_from(settings)?;

        // Start cameras with the given `DeviceConfiguration`
        device.start_cameras(&device_configuration)?;

        // Start IMU if desired
        if settings.desired_streams.imu {
            device.start_imu()?;
        }

        // Get Calibration from the Playback
        let calibration = device.get_calibration(
            device_configuration.depth_mode,
            device_configuration.color_resolution,
        )?;
        // Setup camera internals based on the extracted Calibration
        Self::setup_camera_internals(internals, calibration)?;

        // Update `stream_source` to `Device`
        internals.stream_source = Some(StreamSource::Device(device, device_configuration));

        // Return `DeviceConfiguration` if everything went fine
        Ok(())
    }

    /// Sets up the camera internals from K4A Calibration.
    ///
    /// # Arguments
    /// * `internals` - The internals of the element that contain settings and timestamp internals.
    /// * `calibration` - K4A Calibration of the utilised Device or Playback.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(K4aSrcError)` on failure.
    fn setup_camera_internals(
        internals: &mut K4aSrcInternals,
        calibration: Calibration,
    ) -> Result<(), K4aSrcError> {
        let settings = &internals.settings;
        let camera = &mut internals.camera;

        // Get Transformation if rectification is enabled
        if settings.rectify_depth {
            camera.transformation = Some(Transformation::new(&calibration)?)
        }

        // Serialise the CameraMeta associated with Calibration, if attaching camera meta is desired.
        if settings.attach_camera_meta {
            camera.camera_meta_serialised = Self::extract_camera_meta(settings, &calibration)
                .serialise()
                .map_err(|_err| K4aSrcError::Failure("k4asrc: Cannot serialise camera meta"))?
        }

        // Return Ok if everything went fine
        Ok(())
    }

    /// Determine `StreamProperties`, containing fields relevant for CAPS `fixate()`, based on the
    /// selected `StreamSource`.
    ///
    /// # Arguments
    /// * `stream_source` - The stream source to extract the properties from, i.e. `Playback` or `Device`.
    ///
    /// # Returns
    /// * `Ok(StreamProperties)` on success.
    /// * `Err(K4aSrcError)` on failure.
    fn get_stream_properties(
        stream_source: &StreamSource,
    ) -> Result<StreamProperties, K4aSrcError> {
        Ok(match stream_source {
            StreamSource::Playback(_playback, record_configuration) => {
                // Extract properties from record_configuration is streaming from playback
                StreamProperties::try_from(record_configuration)?
            }
            StreamSource::Device(_device, device_configuration) => {
                // Extract properties from device_configuration if streaming video from device
                StreamProperties::try_from(device_configuration)?
            }
        })
    }

    /// Extract a Capture from either Playback or Device.
    ///
    /// # Arguments
    /// * `internals` - The internals of the element that contain settings and stream source.
    ///
    /// # Returns
    /// * `Ok(Capture)` on success.
    /// * `Err(K4aSrcError)` on failure.
    fn get_capture(internals: &K4aSrcInternals) -> Result<Capture, K4aSrcError> {
        // Extract stream_source and settings from internals
        let stream_source = internals.stream_source.as_ref().unwrap_or_else(|| {
            unreachable!("k4asrc: Stream source is specified before reaching `get_capture()`")
        });
        let settings = &internals.settings;

        Ok(match stream_source {
            StreamSource::Playback(playback, _record_configuration) => {
                // If streaming from a recording, get Capture from Playback
                let mut capture = playback.get_next_capture();
                if settings.playback_settings.loop_recording {
                    // If looping is desired, seek to the beginning once EoF is reached
                    if let Err(K4aError::Eof) = capture {
                        playback.seek_timestamp(0, PlaybackSeekOrigin::K4A_PLAYBACK_SEEK_BEGIN)?;
                        capture = playback.get_next_capture();
                    }
                }
                capture?
            }
            StreamSource::Device(device, _device_configuration) => {
                // If streaming from a physical device, get Capture from Device
                device.get_capture(settings.device_settings.get_capture_timeout)?
            }
        })
    }

    /// Extract all available ImuSamples from either Playback or Device. Unimplemented!
    ///
    /// # Arguments
    /// * `internals` - The internals of the element that contain settings and stream source.
    ///
    /// # Returns
    /// * `Ok(Vec<ImuSample>)` on success.
    /// * `Err(K4aSrcError)` on failure.
    fn get_available_imu_samples(
        internals: &K4aSrcInternals,
    ) -> Result<Vec<ImuSample>, K4aSrcError> {
        // Extract stream_source from internals
        let stream_source = internals.stream_source.as_ref().unwrap_or_else(|| {
            unreachable!(
                "k4asrc: Stream source is specified before reaching `get_available_imu_samples()`"
            )
        });

        // A vector to store all queued ImuSamples
        let mut imu_samples: Vec<ImuSample> = Vec::new();

        match stream_source {
            StreamSource::Playback(_playback, _record_configuration) => {
                // TODO: implement streaming of ImuSamples from recording (synchronisation with capture must be resolved)
                unimplemented!("k4asrc: IMU streaming from Playback is not yet implemented!");
            }
            StreamSource::Device(device, _device_configuration) => {
                // If streaming from a physical device, get samples from Device
                loop {
                    // Loop to obtain all queued ImuSamples
                    let imu_sample = device.get_imu_sample(0);
                    match imu_sample {
                        Ok(imu_sample) => {
                            imu_samples.push(imu_sample);
                        }
                        Err(K4aError::Failure(err_msg)) => {
                            return Err(K4aSrcError::Failure(err_msg));
                        }
                        Err(K4aError::Timeout) => {
                            break;
                        }
                        Err(K4aError::Eof) => {
                            unreachable!("k4asrc: `Device::get_imu_sample()` cannot return Eof")
                        }
                    }
                }
            }
        }
        Ok(imu_samples)
    }

    /// Extract a frame from Capture and attach it to `output_buffer`. This function outputs the
    /// frame as main buffer if `previous_streams` is empty or all `false`. If any of the
    /// `previous_streams` is enabled, the frame is attached as meta buffer.
    ///
    /// # Arguments
    /// * `base_src` - This element (k4asrc).
    /// * `internals` - The internals of the element that contain settings and stream source.
    /// * `output_buffer` - The output buffer to which frames will be attached.
    /// * `capture` - Capture to extract the frames from.
    /// * `stream_id` - The id of the stream to extract.
    /// * `previous_streams` - An indicator of what previous streams are enabled.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(K4aSrcError)` on failure.
    fn attach_frame_to_buffer(
        &self,
        base_src: &gst_base::BaseSrc,
        internals: &mut K4aSrcInternals,
        output_buffer: &mut gst::Buffer,
        capture: &Capture,
        stream_id: &str,
        previous_streams: &[bool],
    ) -> Result<(), K4aSrcError> {
        // Extract the correspond frame from the capture
        let frame = match stream_id {
            STREAM_ID_DEPTH => {
                // Rectify depth, if desired
                if internals.settings.rectify_depth {
                    let depth_image = capture.get_depth_image()?;
                    let transformation = internals.camera
                        .transformation
                        .as_ref()
                        .expect("k4asrc: Transformation for rectification of depth frames is not yet defined.");
                    transformation.depth_image_to_color_camera(depth_image)
                } else {
                    capture.get_depth_image()
                }
            }
            STREAM_ID_IR => capture.get_ir_image(),
            STREAM_ID_COLOR => capture.get_color_image(),
            _ => unreachable!("k4asrc: There are no more video streams available from K4A"),
        }?;

        // Extract buffer out the frame
        let frame_buffer = frame.get_buffer()?;

        // Form a gst buffer out of mutable slice
        let mut buffer = gst::buffer::Buffer::from_mut_slice(frame_buffer);
        // Get mutable reference to the buffer
        let buffer_mut_ref = buffer.get_mut().ok_or(gst_error_msg!(
            gst::ResourceError::Failed,
            [
                "k4asrc: Cannot get mutable reference to {} buffer",
                stream_id
            ]
        ))?;

        // Determine whether any of the previous streams is enabled
        let is_buffer_main = !previous_streams.iter().any(|stream| *stream);

        // Extract timestamp from K4A
        let camera_timestamp = TimestampSource::Image(&frame).extract_timestamp();
        // Set timestamps using `RgbdTimestamps` trait
        self.set_rgbd_timestamp(base_src, buffer_mut_ref, is_buffer_main, camera_timestamp);

        // Where the buffer is placed depends whether this is the first stream that is enabled
        if is_buffer_main {
            // Fill the main buffer and tag it adequately
            rgbd::fill_main_buffer_and_tag(output_buffer, buffer, stream_id)?;
        } else {
            // Attach the secondary buffer and tag it adequately
            rgbd::attach_aux_buffer_and_tag(output_buffer.get_mut().ok_or(gst_error_msg!(
                gst::ResourceError::Failed,
                [
                    "k4asrc: Cannot get mutable reference to the main buffer while attaching {} stream",
                    stream_id
                ]
            ))?, &mut buffer, stream_id)?;
        }

        Ok(())
    }

    /// Attach ImuSamples to `output_buffer`. This function outputs the frame as main buffer if
    /// `previous_streams` is empty or all `false`. If any of the `previous_streams` is enabled,
    /// the frame is attached as meta buffer. Unimplemented!
    ///
    /// # Arguments
    /// * `base_src` - This element (k4asrc).
    /// * `output_buffer` - The output buffer to which the ImuSamples will be attached.
    /// * `imu_samples` - ImuSamples to attach to the `output_buffer`.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(K4aSrcError)` on failure.
    fn attach_imu_samples(
        &self,
        base_src: &gst_base::BaseSrc,
        output_buffer: &mut gst::Buffer,
        imu_samples: Vec<ImuSample>,
    ) -> Result<(), K4aSrcError> {
        // TODO: Determine whether this function can ever return an error
        // Make sure there are samples to push
        if imu_samples.is_empty() {
            gst_warning!(CAT, "No `ImuSample`s were queued");
            return Ok(());
        }

        // Extract timestamp from K4A, based on the first IMU sample
        let camera_timestamp = TimestampSource::ImuSample(&imu_samples[0]).extract_timestamp();

        // Form a gst buffer out of the IMU samples
        let mut buffer = Self::gst_buffer_from_imu_samples(imu_samples)?;
        // Get mutable reference to the buffer
        let buffer_mut_ref = buffer.get_mut().ok_or(gst_error_msg!(
            gst::ResourceError::Failed,
            [
                "k4asrc: Cannot get mutable reference to {} buffer",
                STREAM_ID_IMU
            ]
        ))?;

        // Set timestamps using `RgbdTimestamps` trait
        self.set_rgbd_timestamp(base_src, buffer_mut_ref, false, camera_timestamp);

        // Attach the IMU buffer and tag it adequately
        rgbd::attach_aux_buffer_and_tag(
            output_buffer.get_mut().ok_or(gst_error_msg!(
            gst::ResourceError::Failed,
                [
                    "k4asrc: Cannot get mutable reference to the main buffer while attaching {} stream",
                    STREAM_ID_IMU
                ]
            ))?,
            &mut buffer,
            STREAM_ID_IMU,
        )?;

        Ok(())
    }

    /// Convert/serialise ImuSamples into GStreamer Buffer. Unimplemented!
    ///
    /// # Arguments
    /// * `imu_samples` - ImuSamples to attach to the `output_buffer`.
    ///
    /// # Returns
    /// * `Ok(gst::Buffer)` on success.
    /// * `Err(K4aSrcError)` on failure.
    fn gst_buffer_from_imu_samples(
        _imu_samples: Vec<ImuSample>,
    ) -> Result<gst::Buffer, K4aSrcError> {
        // TODO: implement mapping of `Vec<ImuSample>` to `gst::Buffer`
        unimplemented!(
            "k4asrc: Mapping of `Vec<ImuSample>` to `gst::Buffer` is not yet implemented!"
        );
    }

    /// Attach Cap'n Proto serialised CameraMeta to `output_buffer`.
    ///
    /// # Arguments
    /// * `base_src` - This element (k4asrc).
    /// * `output_buffer` - The output buffer to which the ImuSamples will be attached.
    /// * `camera_meta` - Serialised CameraMeta to attach to the `output_buffer`.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(K4aSrcError)` on failure.
    fn attach_camera_meta(
        &self,
        base_src: &gst_base::BaseSrc,
        output_buffer: &mut gst::Buffer,
        camera_meta: Vec<u8>,
    ) -> Result<(), K4aSrcError> {
        // Form a gst buffer out of mutable slice
        let mut buffer = gst::buffer::Buffer::from_mut_slice(camera_meta);
        // Get mutable reference to the buffer
        let buffer_mut_ref = buffer.get_mut().ok_or(gst_error_msg!(
            gst::ResourceError::Failed,
            [
                "k4asrc: Cannot get mutable reference to {} buffer",
                STREAM_ID_CAMERAMETA
            ]
        ))?;

        // Set timestamps using `RgbdTimestamps` trait
        self.set_rgbd_timestamp(base_src, buffer_mut_ref, false, gst::CLOCK_TIME_NONE);

        // Attach the camera_meta buffer and tag it adequately
        rgbd::attach_aux_buffer_and_tag(
            output_buffer.get_mut().ok_or(gst_error_msg!(
                gst::ResourceError::Failed,
                [
                    "k4asrc: Cannot get mutable reference to the main buffer while attaching {} stream",
                    STREAM_ID_CAMERAMETA
                ]
            ))?,
            &mut buffer,
            STREAM_ID_CAMERAMETA,
        )?;

        Ok(())
    }

    /// Convert K4A Calibration into CameraMeta while taking settings, e.g. enabled streams, into consideration.
    ///
    /// # Arguments
    /// * `settings` - Settings of the element.
    /// * `calibration` - Calibration of the utilised Device or Playback.
    ///
    /// # Returns
    /// * `CameraMeta` containing the appropriate parameters.
    fn extract_camera_meta(settings: &Settings, calibration: &Calibration) -> CameraMeta {
        // Get the depth and color camera calibration
        let depth_calibration = calibration.depth_camera_calibration();
        let color_calibration = calibration.color_camera_calibration();

        // Create intrinsics and insert the appropriate streams
        let intrinsics = Self::extract_intrinsics(
            settings.desired_streams,
            &depth_calibration,
            &color_calibration,
        );

        // Create extrinsics and insert the appropriate transformations
        let extrinsics = Self::extract_extrinsics(settings.desired_streams, &calibration);

        // K4A Depth is always in millimetres (0.001), due to its DEPTH16 K4A format.
        CameraMeta::new(intrinsics, extrinsics, 0.001)
    }

    /// Extract Intrinsics from K4A Calibration.
    ///
    /// # Arguments
    /// * `desired_streams` - Desired streams.
    /// * `depth_calibration` - Calibration of the depth camera.
    /// * `color_calibration` - Calibration of the color camera.
    ///
    /// # Returns
    /// * `HashMap<String, camera_meta::Intrinsics>` containing Intrinsics corresponding to a stream.
    fn extract_intrinsics(
        desired_streams: Streams,
        depth_calibration: &CameraCalibration,
        color_calibration: &CameraCalibration,
    ) -> HashMap<String, camera_meta::Intrinsics> {
        let mut intrinsics: HashMap<String, camera_meta::Intrinsics> = HashMap::new();
        if desired_streams.depth {
            intrinsics.insert(
                STREAM_ID_DEPTH.to_string(),
                Self::k4a_intrinsics_to_camera_meta_intrinsics(&depth_calibration.intrinsics),
            );
        }
        if desired_streams.ir {
            intrinsics.insert(
                STREAM_ID_IR.to_string(),
                Self::k4a_intrinsics_to_camera_meta_intrinsics(&depth_calibration.intrinsics),
            );
        }
        if desired_streams.color {
            intrinsics.insert(
                STREAM_ID_COLOR.to_string(),
                Self::k4a_intrinsics_to_camera_meta_intrinsics(&color_calibration.intrinsics),
            );
        }
        intrinsics
    }

    /// Extract Entrinsics from K4A Calibration.
    ///
    /// # Arguments
    /// * `desired_streams` - Desired streams.
    /// * `calibration` - Calibration of the utilised Device or Playback.
    ///
    /// # Returns
    /// * `HashMap<(String, String), camera_meta::Transformation>` containing Transformation
    /// in a hashmap of <(from, to), Transformation>.
    fn extract_extrinsics(
        desired_streams: Streams,
        calibration: &Calibration,
    ) -> HashMap<(String, String), camera_meta::Transformation> {
        // Create extrinsics and insert the appropriate transformations
        let mut extrinsics: HashMap<(String, String), camera_meta::Transformation> = HashMap::new();

        // Determine the main stream from which all extrinsics are computed
        let main_stream = Self::determine_main_stream(desired_streams);
        let main_stream_calibration_type =
            Self::determine_main_stream_calibration_type(desired_streams);

        // Insert extrinsics from main stream to the IR, unless it is the main stream itself
        if desired_streams.ir && main_stream != STREAM_ID_IR {
            extrinsics.insert(
                (main_stream.to_string(), STREAM_ID_IR.to_string()),
                Self::k4a_extrinsics_to_camera_meta_transformation(
                    calibration
                        .extrinsics(main_stream_calibration_type, K4A_CALIBRATION_TYPE_DEPTH),
                ),
            );
        }

        // Insert extrinsics from main stream to the color, unless it is the main stream itself
        if desired_streams.color && main_stream != STREAM_ID_COLOR {
            extrinsics.insert(
                (main_stream.to_string(), STREAM_ID_COLOR.to_string()),
                Self::k4a_extrinsics_to_camera_meta_transformation(
                    calibration
                        .extrinsics(main_stream_calibration_type, K4A_CALIBRATION_TYPE_COLOR),
                ),
            );
        }

        // Insert extrinsics from main stream to the IMU, for both gyroscope and accelerometer
        if desired_streams.imu {
            extrinsics.insert(
                (main_stream.to_string(), format!("{}_gyro", STREAM_ID_IMU)),
                Self::k4a_extrinsics_to_camera_meta_transformation(
                    calibration.extrinsics(main_stream_calibration_type, K4A_CALIBRATION_TYPE_GYRO),
                ),
            );
            extrinsics.insert(
                (main_stream.to_string(), format!("{}_accel", STREAM_ID_IMU)),
                Self::k4a_extrinsics_to_camera_meta_transformation(
                    calibration
                        .extrinsics(main_stream_calibration_type, K4A_CALIBRATION_TYPE_ACCEL),
                ),
            );
        }
        extrinsics
    }

    /// Convert K4A Intrinsics into CameraMeta Intrinsics.
    ///
    /// # Arguments
    /// * `k4a_intrinsics` - K4a intrinsics to convert.
    ///
    /// # Returns
    /// * `camera_meta::Intrinsics` containing the converted intrinsics.
    fn k4a_intrinsics_to_camera_meta_intrinsics(
        k4a_intrinsics: &k4a::intrinsics::Intrinsics,
    ) -> camera_meta::Intrinsics {
        use k4a::CalibrationModelType::*;
        let c = &k4a_intrinsics.parameters;
        let distortion = match k4a_intrinsics.type_ {
            K4A_CALIBRATION_LENS_DISTORTION_MODEL_BROWN_CONRADY => Distortion::K4aBrownConrady(
                camera_meta::K4aCoefficients::new(c.k1, c.k2, c.k3, c.k4, c.k5, c.k6, c.p1, c.p2),
            ),
            // THETA, POLYNOMIAL_3K and RATIONAL_6KT are deprecated
            K4A_CALIBRATION_LENS_DISTORTION_MODEL_UNKNOWN
            | K4A_CALIBRATION_LENS_DISTORTION_MODEL_THETA
            | K4A_CALIBRATION_LENS_DISTORTION_MODEL_POLYNOMIAL_3K
            | K4A_CALIBRATION_LENS_DISTORTION_MODEL_RATIONAL_6KT => {
                gst_warning!(
                    CAT,
                    "One of the K4A cameras utilises an unknown or deprecated distorion model.",
                );
                Distortion::Unknown
            }
        };
        camera_meta::Intrinsics {
            fx: c.fx,
            fy: c.fy,
            cx: c.cx,
            cy: c.cy,
            distortion,
        }
    }

    /// Convert K4A Extrinsics into CameraMeta Transformation, which is used for creation of camera_meta::Extrinsics.
    ///
    /// # Arguments
    /// * `k4a_extrinsics` - K4a extrinsics to convert.
    ///
    /// # Returns
    /// * `camera_meta::Transformation` containing the converted transformation.
    fn k4a_extrinsics_to_camera_meta_transformation(
        k4a_extrinsics: k4a::extrinsics::Extrinsics,
    ) -> camera_meta::Transformation {
        camera_meta::Transformation::new(
            camera_meta::Translation::from(k4a_extrinsics.translation),
            camera_meta::RotationMatrix::from(k4a_extrinsics.rotation),
        )
    }

    /// Determine the main stream, while taking into account the priority `depth > ir > color`, and return the corresponding ID.
    ///
    /// # Arguments
    /// * `streams` - Struct containing enabled streams.
    ///
    /// # Returns
    /// * `&str` containing the ID of the main stream.
    fn determine_main_stream(streams: Streams) -> &'static str {
        if streams.depth {
            STREAM_ID_DEPTH
        } else if streams.ir {
            STREAM_ID_IR
        } else {
            STREAM_ID_COLOR
        }
    }

    /// Determine the calibration type of the main stream, while taking into account the priority `depth == ir > color`.
    /// This function is useful for extracting Extrinsics from k4a::Calibration.
    ///
    /// # Arguments
    /// * `streams` - Struct containing enabled streams.
    ///
    /// # Returns
    /// * `k4a::CalibrationType` containing the corresponding calibration type.
    fn determine_main_stream_calibration_type(streams: Streams) -> k4a::CalibrationType {
        if streams.depth | streams.ir {
            K4A_CALIBRATION_TYPE_DEPTH
        } else {
            K4A_CALIBRATION_TYPE_COLOR
        }
    }
}

impl RgbdTimestamps for K4aSrc {
    fn get_timestamp_internals(&self) -> Arc<Mutex<TimestampInternals>> {
        self.timestamp_internals.clone()
    }
}

impl ElementImpl for K4aSrc {}

impl ObjectImpl for K4aSrc {
    glib_object_impl!();

    fn constructed(&self, obj: &glib::Object) {
        // Chain up parent implementation
        self.parent_constructed(obj);

        // Make the source live with time-based format
        let element = obj
            .downcast_ref::<gst_base::BaseSrc>()
            .expect("k4asrc: Cannot cast to BaseSrc");

        // Set format to time
        element.set_format(gst::Format::Time);

        // The element is live by default, but can be changed to false once `recording-location`
        // is defined and `real-time-playback=false`
        element.set_live(true);
    }

    fn get_property(&self, _obj: &glib::Object, id: usize) -> Result<glib::Value, ()> {
        // Get settings
        let settings = &self
            .internals
            .lock()
            .expect("k4asrc: Cannot lock internals in `get_property()`")
            .settings;

        let prop = &PROPERTIES[id];
        match *prop {
            subclass::Property("serial", ..) => Ok(settings.device_settings.serial.to_value()),
            subclass::Property("recording-location", ..) => {
                Ok(settings.playback_settings.recording_location.to_value())
            }
            subclass::Property("enable-depth", ..) => Ok(settings.desired_streams.depth.to_value()),
            subclass::Property("enable-ir", ..) => Ok(settings.desired_streams.ir.to_value()),
            subclass::Property("enable-color", ..) => Ok(settings.desired_streams.color.to_value()),
            subclass::Property("enable-imu", ..) => Ok(settings.desired_streams.imu.to_value()),
            subclass::Property("color-format", ..) => {
                Ok(settings.device_settings.color_format.to_value())
            }
            subclass::Property("color-resolution", ..) => {
                Ok(settings.device_settings.color_resolution.to_value())
            }
            subclass::Property("depth-mode", ..) => {
                Ok(settings.device_settings.depth_mode.to_value())
            }
            subclass::Property("framerate", ..) => {
                Ok(settings.device_settings.framerate.to_value())
            }
            subclass::Property("get-capture-timeout", ..) => {
                Ok(settings.device_settings.get_capture_timeout.to_value())
            }
            subclass::Property("loop-recording", ..) => {
                Ok(settings.playback_settings.loop_recording.to_value())
            }
            subclass::Property("real-time-playback", ..) => {
                Ok(settings.playback_settings.loop_recording.to_value())
            }
            subclass::Property("rectify-depth", ..) => Ok(settings.rectify_depth.to_value()),
            subclass::Property("attach-camera-meta", ..) => {
                Ok(settings.attach_camera_meta.to_value())
            }
            subclass::Property("timestamp-mode", ..) => Ok(self
                .get_timestamp_internals()
                .lock()
                .unwrap()
                .timestamp_mode
                .to_value()),
            _ => unimplemented!("k4asrc: Property is not implemented"),
        }
    }

    fn set_property(&self, obj: &glib::Object, id: usize, value: &glib::Value) {
        let element = obj
            .downcast_ref::<gst_base::BaseSrc>()
            .expect("k4asrc: Could not cast k4asrc to BaseSrc");

        // Get settings
        let settings = &mut self
            .internals
            .lock()
            .expect("k4asrc: Cannot lock internals in `set_property()`")
            .settings;

        let property = &PROPERTIES[id];
        match *property {
            subclass::Property("serial", ..) => {
                let serial = value
                    .get()
                    .unwrap_or_else(|err| {
                        panic!(
                            "k4asrc: Failed to set property `serial` due to incorrect type: {:?}",
                            err
                        )
                    })
                    .unwrap_or_default();
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `serial` from {:?} to {:?}",
                    settings.device_settings.serial,
                    serial
                );
                settings.device_settings.serial = serial;
                // Streaming from Device makes this source always live
                obj.downcast_ref::<gst_base::BaseSrc>()
                    .unwrap()
                    .set_live(true);
            }
            subclass::Property("recording-location", ..) => {
                let mut recording_location = value
                    .get()
                    .unwrap_or_else(|err| {
                        panic!("k4asrc: Failed to set property `recording-location` due to incorrect type: {:?}", err)
                    })
                    .unwrap_or_default();
                expand_tilde_as_home_dir(&mut recording_location);
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `recording-location` from {:?} to {:?}",
                    settings.playback_settings.recording_location,
                    recording_location
                );
                settings.playback_settings.recording_location = recording_location;
                // Liveliness of the element, when streaming from Playback, depends also on `real-time-playback` property
                if !settings.playback_settings.recording_location.is_empty() {
                    obj.downcast_ref::<gst_base::BaseSrc>()
                        .unwrap()
                        .set_live(settings.playback_settings.real_time_playback);
                }
            }
            subclass::Property("enable-depth", ..) => {
                let enable_depth = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "k4asrc: Failed to set property `enable-depth` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `enable-depth` from {} to {}",
                    settings.desired_streams.depth,
                    enable_depth
                );
                settings.desired_streams.depth = enable_depth;
            }
            subclass::Property("enable-ir", ..) => {
                let enable_ir = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "k4asrc: Failed to set property `enable-ir` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `enable-ir` from {} to {}",
                    settings.desired_streams.ir,
                    enable_ir
                );
                settings.desired_streams.ir = enable_ir;
            }
            subclass::Property("enable-color", ..) => {
                let enable_color = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "k4asrc: Failed to set property `enable-color` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `enable-color` from {} to {}",
                    settings.desired_streams.color,
                    enable_color
                );
                settings.desired_streams.color = enable_color;
            }
            subclass::Property("enable-imu", ..) => {
                let enable_imu = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "k4asrc: Failed to set property `enable-imu` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `enable-imu` from {} to {}",
                    settings.desired_streams.imu,
                    enable_imu
                );
                settings.desired_streams.imu = enable_imu;
            }
            subclass::Property("color-format", ..) => {
                let color_format = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "k4asrc: Failed to set property `color-format` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `color-format` from {:?} to {:?}",
                    settings.device_settings.color_format,
                    color_format
                );
                settings.device_settings.color_format = color_format;
            }
            subclass::Property("color-resolution", ..) => {
                let color_resolution = value.get_some().unwrap_or_else(|err| panic!("k4asrc: Failed to set property `color-resolution` due to incorrect type: {:?}", err));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `color-resolution` from {:?} to {:?}",
                    settings.device_settings.color_resolution,
                    color_resolution
                );
                settings.device_settings.color_resolution = color_resolution;
            }
            subclass::Property("depth-mode", ..) => {
                let depth_mode = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "k4asrc: Failed to set property `depth-mode` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `depth-mode` from {:?} to {:?}",
                    settings.device_settings.depth_mode,
                    depth_mode
                );
                settings.device_settings.depth_mode = depth_mode;
            }
            subclass::Property("framerate", ..) => {
                let framerate = value.get_some().unwrap_or_else(|err| {
                    panic!(
                        "k4asrc: Failed to set property `framerate` due to incorrect type: {:?}",
                        err
                    )
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `framerate` from {:?} to {:?}",
                    settings.device_settings.framerate,
                    framerate
                );
                settings.device_settings.framerate = framerate;
            }
            subclass::Property("get-capture-timeout", ..) => {
                let get_capture_timeout = value.get_some().unwrap_or_else(|err| panic!("k4asrc: Failed to set property `get-capture-timeout` due to incorrect type: {:?}", err));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `get-capture-timeout` from {} to {}",
                    settings.device_settings.get_capture_timeout,
                    get_capture_timeout
                );
                settings.device_settings.get_capture_timeout = get_capture_timeout;
            }
            subclass::Property("loop-recording", ..) => {
                let loop_recording = value.get_some().unwrap_or_else(|err| panic!("k4asrc: Failed to set property `loop-recording` due to incorrect type: {:?}", err));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `loop-recording` from {} to {}",
                    settings.playback_settings.loop_recording,
                    loop_recording
                );
                settings.playback_settings.loop_recording = loop_recording;
            }
            subclass::Property("real-time-playback", ..) => {
                let real_time_playback = value.get_some().unwrap_or_else(|err| panic!("k4asrc: Failed to set property `real-time-playback` due to incorrect type: {:?}", err));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `real-time-playback` from {} to {}",
                    settings.playback_settings.real_time_playback,
                    real_time_playback
                );
                settings.playback_settings.real_time_playback = real_time_playback;
                // Make sure that streaming from playback is enabled before changing the liveliness of the element
                if !settings.playback_settings.recording_location.is_empty() {
                    obj.downcast_ref::<gst_base::BaseSrc>()
                        .unwrap()
                        .set_live(settings.playback_settings.real_time_playback);
                }
            }
            subclass::Property("rectify-depth", ..) => {
                let rectify_depth = value.get_some().unwrap_or_else(|err| panic!("k4asrc: Failed to set property `rectify-depth` due to incorrect type: {:?}", err));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `rectify-depth` from {} to {}",
                    settings.desired_streams.depth,
                    rectify_depth
                );
                settings.rectify_depth = rectify_depth;
            }
            subclass::Property("attach-camera-meta", ..) => {
                let attach_camera_meta = value.get_some().unwrap_or_else(|err| panic!("k4asrc: Failed to set property `attach-camera-meta` due to incorrect type: {:?}", err));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `attach-camera-meta` from {} to {}",
                    settings.attach_camera_meta,
                    attach_camera_meta
                );
                settings.attach_camera_meta = attach_camera_meta;
            }
            subclass::Property("timestamp-mode", ..) => {
                let timestamp_mode = value.get_some()
                    .unwrap_or_else(|err| panic!("k4asrc: Failed to set property `timestamp-mode` due to incorrect type: {:?}", err));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `timestamp-mode`  to {:?}",
                    timestamp_mode
                );
                self.set_timestamp_mode(element, timestamp_mode);
            }
            _ => unimplemented!("k4asrc: Property is not implemented"),
        };
    }
}

/// Helper function that replaces "~/" at the beginning of `path` with "$HOME/",
/// while `path` remains unchanged if it does not start with "~/".
fn expand_tilde_as_home_dir(path: &mut String) {
    if path.starts_with("~/") {
        let home_path = std::env::var("HOME")
        .expect("k4asrc: $HOME must be specified if a path for property is specified with \"~\" (tilde).");
        path.replace_range(..1, &home_path);
    }
}

pub fn register(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    gst::Element::register(Some(plugin), "k4asrc", gst::Rank::None, K4aSrc::get_type())
}
