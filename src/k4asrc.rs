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

use crate::error::*;
use crate::properties::*;
use crate::settings::*;
use crate::stream_properties::*;
use crate::streams::*;
use crate::timestamps::*;
use crate::utilities::*;
use glib::subclass;
use gst::subclass::prelude::*;
use gst_base::prelude::*;
use gst_base::subclass::prelude::*;
use gst_depth_meta::buffer::BufferMeta;
use gst_depth_meta::tags::TagsMeta;
use k4a::capture::Capture;
use k4a::device::Device;
use k4a::error::K4aError;
use k4a::imu_sample::ImuSample;
use k4a::playback::Playback;
use k4a::utilities::*;
use k4a::*;
use std::sync::Mutex;

/// A struct representation of the `k4asrc` element.
struct K4aSrc {
    /// Internals of `k4asrc` element that are locked under mutex.
    internals: Mutex<K4aSrcInternals>,
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
    /// Contains initial timestamps for each stream as well as frame duration.
    timestamp_internals: TimestampInternals,
}

/// An enum that contains information about stream source from either playback and physical K4A device.
enum StreamSource {
    /// Variant that contains information about playback stream source.
    Playback(Playback, RecordConfiguration),
    /// Variant that contains information about device stream source.
    Device(Device, DeviceConfiguration),
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
        klass.install_properties(&PROPERTIES);

        // Create src pad template with `video/rgbd` caps
        let src_caps = gst::Caps::new_simple(
            "video/rgbd",
            &[
                // A list of the available K4A streams, indicating their respective priority
                (
                    "streams",
                    &format! {"{},{},{},{}", STREAM_ID_DEPTH, STREAM_ID_IR, STREAM_ID_COLOR, STREAM_ID_IMU},
                ),
                (
                    // Framerates at which K4A is capable of providing stream
                    "framerate",
                    &gst::List::new(&[
                        &gst::Fraction::new(ALLOWED_FRAMERATES[0], 1),
                        &gst::Fraction::new(ALLOWED_FRAMERATES[1], 1),
                        &gst::Fraction::new(ALLOWED_FRAMERATES[2], 1),
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
                timestamp_internals: TimestampInternals {
                    frame_duration: gst::CLOCK_TIME_NONE,
                    common_timestamp: gst::CLOCK_TIME_NONE,
                    first_frame_timestamp: gst::CLOCK_TIME_NONE,
                },
            }),
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
        self.start_k4a(internals)?;

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

    fn fixate(&self, base_src: &gst_base::BaseSrc, caps: gst::Caps) -> gst::Caps {
        // Lock the internals
        let internals = &mut self
            .internals
            .lock()
            .expect("k4asrc: Cannot lock internals in `fixate()`");
        let desired_streams = &internals.settings.desired_streams;

        let mut caps = gst::Caps::truncate(caps);
        {
            // Map caps to mutable structure
            let caps = caps
                .make_mut()
                .get_mut_structure(0)
                .expect("k4asrc: Failed to map caps to mutable structure");
            // Fixate based on stream source
            let stream_properties = self
                .get_stream_properties(internals.stream_source.as_ref().unwrap_or_else(|| {
                    unreachable!("k4asrc: Stream source is specified before reaching `fixate()`")
                }))
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
                    &k4a_image_format_to_gst_video_format(&DEPTH_FORMAT)
                        .unwrap()
                        .to_string(),
                );
                caps.set(
                    &format!("{}_width", STREAM_ID_DEPTH),
                    &stream_properties.depth_resolution.width,
                );
                caps.set(
                    &format!("{}_height", STREAM_ID_DEPTH),
                    &stream_properties.depth_resolution.height,
                );
            }
            // Add ir stream with its format, width and height into the caps, if enabled
            if desired_streams.ir {
                selected_streams.push_str(&format!("{},", STREAM_ID_IR));
                caps.set(
                    &format!("{}_format", STREAM_ID_IR),
                    &k4a_image_format_to_gst_video_format(&IR_FORMAT)
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

            // Pop the last ',' contained in streams (not really necessary, but nice)
            selected_streams.pop();
            // Fixate the framerate
            caps.fixate_field_nearest_fraction("framerate", stream_properties.framerate);

            internals.timestamp_internals.frame_duration = gst::ClockTime::from_nseconds(
                std::time::Duration::from_secs_f32(1.0_f32 / stream_properties.framerate as f32)
                    .as_nanos() as u64,
            );

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
        _length: u32,
    ) -> Result<gst::Buffer, gst::FlowError> {
        // Lock the internals
        let internals = &mut self
            .internals
            .lock()
            .expect("k4asrc: Cannot lock internals in `create()`");
        let desired_streams = internals.settings.desired_streams;

        // Create the output buffer
        let mut output_buffer = gst::buffer::Buffer::new();

        let capture = self.get_capture(internals)?;
        // Attach `depth` frame if enabled
        if desired_streams.depth {
            self.attach_frame_to_buffer(
                base_src,
                internals,
                &mut output_buffer,
                &capture,
                STREAM_ID_DEPTH,
                &[],
            )?;
        }

        // Attach `ir` frame if enabled
        if desired_streams.ir {
            self.attach_frame_to_buffer(
                base_src,
                internals,
                &mut output_buffer,
                &capture,
                STREAM_ID_IR,
                &[desired_streams.depth],
            )?;
        }

        // Attach `color` frame if enabled
        if desired_streams.color {
            self.attach_frame_to_buffer(
                base_src,
                internals,
                &mut output_buffer,
                &capture,
                STREAM_ID_COLOR,
                &[desired_streams.depth, desired_streams.ir],
            )?;
        }

        // Attach `IMU` samples if enabled
        if desired_streams.imu {
            let imu_samples = self.get_available_imu_samples(internals)?;
            self.attach_imu_samples(base_src, internals, &mut output_buffer, imu_samples)?;
        }

        Ok(output_buffer)
    }

    fn is_seekable(&self, _base_src: &gst_base::BaseSrc) -> bool {
        // TODO: If desired, enable seeking for streaming from `Playback`
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
    fn start_k4a(&self, internals: &mut K4aSrcInternals) -> Result<(), K4aSrcError> {
        // Extract `desired_streams` and `stream_source` from `internals`
        let settings = &internals.settings;
        let stream_source = &mut internals.stream_source;

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

        // Determine whether to stream `Playback`
        if !settings.playback_settings.recording_location.is_empty() {
            // Open `Playback`
            let playback = Playback::open(&settings.playback_settings.recording_location)?;
            // Configure streaming based on the opened `Playback`
            let record_configuration = self.start_from_playback(&settings, &playback)?;
            // Update `stream_source` to `Playback`
            *stream_source = Some(StreamSource::Playback(playback, record_configuration));

            // Return `Ok()` if everything went fine and start streaming from `Playback`
            return Ok(());
        }

        // If `file_path` is not set, live stream from `Device` is assumed
        // Open a `Device`
        let device = if !settings.device_settings.serial.is_empty() {
            // Open `Device` based on its `serial` number
            Device::open_with_serial(&settings.device_settings.serial)?
        } else {
            // If no serial is specified, open the first connected `Device`
            Device::open(0)?
        };
        // Configure streaming for the opened `Device`
        let device_configuration = self.start_from_device(&settings, &device)?;

        // Update `stream_source` to `Device`
        *stream_source = Some(StreamSource::Device(device, device_configuration));
        // Return `Ok()` if everything went fine and start streaming from `Device`
        Ok(())
    }

    /// Start streaming from K4A `Playback`.
    ///
    /// # Arguments
    /// * `settings` - The setting of the element.
    /// * `playback` - The Playback to start streaming from.
    ///
    /// # Returns
    /// * `Ok(RecordConfiguration)` on success.
    /// * `Err(K4aSrcError)` on failure.
    fn start_from_playback(
        &self,
        settings: &Settings,
        playback: &Playback,
    ) -> Result<RecordConfiguration, K4aSrcError> {
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
        if !Streams::are_streams_available(&settings.desired_streams, &available_streams) {
            return Err(K4aSrcError::Failure(
                "k4asrc: Some of the desired stream(s) are not available in the recording for playback",
            ));
        }

        // Return `Ok()` if everything went fine
        Ok(record_configuration)
    }

    /// Start streaming from K4A `Device`.
    ///
    /// # Arguments
    /// * `settings` - The setting of the element.
    /// * `device` - The Device to start streaming from.
    ///
    /// # Returns
    /// * `Ok(DeviceConfiguration)` on success.
    /// * `Err(K4aSrcError)` on failure.
    fn start_from_device(
        &self,
        settings: &Settings,
        device: &Device,
    ) -> Result<DeviceConfiguration, K4aSrcError> {
        // Create `DeviceConfiguration` based on settings
        let device_configuration = DeviceConfiguration::try_from(settings)?;

        // Start cameras with the given `DeviceConfiguration`
        device.start_cameras(&device_configuration)?;

        // Start IMU if desired
        if settings.desired_streams.imu {
            device.start_imu()?;
        }

        // Return `DeviceConfiguration` if everything went fine
        Ok(device_configuration)
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
        &self,
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
    fn get_capture(&self, internals: &K4aSrcInternals) -> Result<Capture, K4aSrcError> {
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
        &self,
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
        // Extract the correspond buffer from the capture
        let frame = match stream_id {
            STREAM_ID_DEPTH => capture.get_depth_image(),
            STREAM_ID_IR => capture.get_ir_image(),
            STREAM_ID_COLOR => capture.get_color_image(),
            _ => unreachable!("k4asrc: There are no more video streams"),
        };
        let frame_buffer = frame.get_buffer()?;
        // Form a gst buffer out of mutable slice
        let mut buffer = gst::buffer::Buffer::from_mut_slice(frame_buffer);
        // Get mutable reference to the buffer
        let buffer_mut_ref = buffer.get_mut().expect(&format!(
            "k4asrc: Cannot get mutable reference to {} buffer",
            stream_id
        ));

        // Determine whether any of the previous streams is enabled
        let is_buffer_main = !previous_streams.iter().any(|s| *s);

        // Set buffer duration
        buffer_mut_ref.set_duration(internals.timestamp_internals.frame_duration);

        // Set timestamps if desired, based on timestamp_mode
        let timestamp = self.determine_timestamp(
            base_src,
            internals,
            is_buffer_main,
            TimestampSource::Image(&frame),
        );
        if timestamp != gst::CLOCK_TIME_NONE {
            buffer_mut_ref.set_pts(timestamp);
            buffer_mut_ref.set_dts(timestamp);
        }

        // Create an appropriate tag
        let mut tags = gst::tags::TagList::new();
        tags.get_mut()
            .expect(&format!(
                "k4asrc: Cannot get mutable reference to {} tags",
                stream_id
            ))
            .add::<gst::tags::Title>(&stream_id, gst::TagMergeMode::Append);

        // Where the buffer is placed depends whether this is the first stream that is enabled
        if is_buffer_main {
            // Else put this frame into the output buffer
            *output_buffer = buffer;
            // Add the tag
            TagsMeta::add(
                output_buffer
                    .get_mut()
                    .expect("k4asrc: Cannot get mutable reference to output buffer"),
                &mut tags,
            );
        } else {
            // Add tag to this new buffer
            TagsMeta::add(buffer_mut_ref, &mut tags);
            // Attach this new buffer as meta to the output buffer
            BufferMeta::add(
                output_buffer
                    .get_mut()
                    .expect("k4asrc: Cannot get mutable reference to output buffer"),
                &mut buffer,
            );
        }

        Ok(())
    }

    /// Attach ImuSamples to `output_buffer`. This function outputs the frame as main buffer if
    /// `previous_streams` is empty or all `false`. If any of the `previous_streams` is enabled,
    /// the frame is attached as meta buffer. Unimplemented!
    ///
    /// # Arguments
    /// * `internals` - The internals of the element that contain settings and stream source.
    /// * `output_buffer` - The output buffer to which the ImuSamples will be attached.
    /// * `imu_samples` - ImuSamples to attach to the `output_buffer`.
    /// * `previous_streams` - An indicator of what previous streams are enabled.
    ///
    /// # Returns
    /// * `Ok()` on success.
    /// * `Err(K4aSrcError)` on failure.
    fn attach_imu_samples(
        &self,
        base_src: &gst_base::BaseSrc,
        internals: &mut K4aSrcInternals,
        output_buffer: &mut gst::Buffer,
        imu_samples: Vec<ImuSample>,
    ) -> Result<(), K4aSrcError> {
        // Make sure there are samples to push
        if imu_samples.is_empty() {
            gst_warning!(CAT, "No `ImuSample`s were queued");
            return Ok(());
        }

        // Determine timestamps based on timestamp_mode
        let timestamp = self.determine_timestamp(
            base_src,
            internals,
            false,
            TimestampSource::ImuSample(&imu_samples[0]),
        );

        // Form a gst buffer out of the IMU samples
        let mut buffer = self.gst_buffer_from_imu_samples(imu_samples)?;
        // Get mutable reference to the buffer
        let buffer_mut_ref = buffer.get_mut().expect(&format!(
            "k4asrc: Cannot get mutable reference to IMU buffer",
        ));

        // Set buffer duration
        buffer_mut_ref.set_duration(internals.timestamp_internals.frame_duration);
        // Set timestamp
        if timestamp != gst::CLOCK_TIME_NONE {
            buffer_mut_ref.set_pts(timestamp);
            buffer_mut_ref.set_dts(timestamp);
        }

        // Create an appropriate tag
        let mut tags = gst::tags::TagList::new();
        tags.get_mut()
            .expect(&format!(
                "k4asrc: Cannot get mutable reference to {} tags",
                STREAM_ID_IMU
            ))
            .add::<gst::tags::Title>(&STREAM_ID_IMU, gst::TagMergeMode::Append);

        // Add tag to this new buffer
        TagsMeta::add(buffer_mut_ref, &mut tags);
        // Attach this new buffer as meta to the output buffer
        BufferMeta::add(
            output_buffer
                .get_mut()
                .expect("k4asrc: Cannot get mutable reference to output buffer"),
            &mut buffer,
        );
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
        &self,
        _imu_samples: Vec<ImuSample>,
    ) -> Result<gst::Buffer, K4aSrcError> {
        // TODO: implement mapping of `Vec<ImuSample>` to `gst::Buffer`
        unimplemented!(
            "k4asrc: Mapping of `Vec<ImuSample>` to `gst::Buffer` is not yet implemented!"
        );
    }

    /// Determine the timestamp to use for a buffer based on the selected `timestamp-mode`.
    ///
    /// # Arguments
    /// * `base_src` - This element (k4asrc).
    /// * `internals` - The internals of the element that contain settings and timestamp internals.
    /// * `is_buffer_main` - A flag that determines whether the buffer is main or not.
    /// Useful for `TimestampMode::All` and `TimestampMode::K4aCommon` modes.
    /// * `timestamp_source` -  Contains struct that can be used for extraction of timestamps.
    /// Useful for `TimestampMode::K4aCommon` and `TimestampMode::K4aIndividual` modes.
    ///
    /// # Returns
    /// * `gst::ClockTime` containing the timestamp or gst::CLOCK_TIME_NONE if the selected mode
    /// does not require timestamp.
    fn determine_timestamp(
        &self,
        base_src: &gst_base::BaseSrc,
        internals: &mut K4aSrcInternals,
        is_buffer_main: bool,
        timestamp_source: TimestampSource,
    ) -> gst::ClockTime {
        let timestamp_mode = internals.settings.timestamp_mode;
        // Proceed based on the selected timestamp mode
        match timestamp_mode {
            TimestampMode::Ignore | TimestampMode::Main => {
                // Return `CLOCK_TIME_NONE`
                //     Variant `TimestampMode::Ignore` does not require timestamps
                //     Variant `TimestampMode::Main` is handled by the parent class
                gst::CLOCK_TIME_NONE
            }
            TimestampMode::All => {
                // Determine common timestamp (computed only once for the main buffer)
                if is_buffer_main {
                    // Use element's clock during the computation
                    internals.timestamp_internals.common_timestamp = if let Some(element_clock) =
                        base_src.get_clock()
                    {
                        element_clock.get_time() - base_src.get_base_time()
                    } else {
                        gst_warning!(
                            CAT,
                            obj: base_src,
                            "Element has no clock, unable to determine timestamps for `timestamp-mode=all`",
                                    );
                        gst::CLOCK_TIME_NONE
                    }
                }

                // Return the common timestamp
                internals.timestamp_internals.common_timestamp
            }
            TimestampMode::K4aCommon => {
                // Determine common timestamp (computed only once for the main buffer)
                if is_buffer_main {
                    // Use K4A timestamp of Image/ImuSample during the computation
                    let frame_timestamp = timestamp_source.extract_timestamp();

                    // Initialise the base time, i.e. timestamp of the first frame
                    let base_time = &mut internals.timestamp_internals.first_frame_timestamp;
                    if *base_time == gst::CLOCK_TIME_NONE {
                        *base_time = frame_timestamp;
                    }

                    // Use K4A timestamp of Image/ImuSample during the computation
                    internals.timestamp_internals.common_timestamp = frame_timestamp - *base_time
                }

                // Return the common timestamp
                internals.timestamp_internals.common_timestamp
            }
            TimestampMode::K4aIndividual => {
                // Use K4A timestamp of each Image/ImuSample during the computation
                let frame_timestamp = timestamp_source.extract_timestamp();

                // Initialise the base time, i.e. timestamp of the first frame
                let base_time = &mut internals.timestamp_internals.first_frame_timestamp;
                if *base_time == gst::CLOCK_TIME_NONE {
                    *base_time = frame_timestamp;
                }

                // Compute timestamp since base_time and apply
                frame_timestamp - *base_time
            }
        }
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

        // The element is live by default, but changes to false once `recording-location` is defined.
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
                Ok((settings.device_settings.color_format as i32).to_value())
            }
            subclass::Property("color-resolution", ..) => {
                Ok((settings.device_settings.color_resolution as i32).to_value())
            }
            subclass::Property("depth-mode", ..) => {
                Ok((settings.device_settings.depth_mode as i32).to_value())
            }
            subclass::Property("framerate", ..) => {
                Ok(settings.device_settings.framerate.to_value())
            }
            subclass::Property("loop-recording", ..) => {
                Ok(settings.playback_settings.loop_recording.to_value())
            }
            subclass::Property("get-capture-timeout", ..) => {
                Ok(settings.device_settings.get_capture_timeout.to_value())
            }
            subclass::Property("timestamp-mode", ..) => {
                Ok((settings.timestamp_mode as i32).to_value())
            }
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
                let serial = value.get().expect(&format!(
                    "k4asrc: Failed to set property `serial`. Expected a `string`, but got: {:?}",
                    value
                ));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `serial` from {:?} to {:?}",
                    settings.device_settings.serial,
                    serial
                );
                settings.device_settings.serial = serial;
                obj.downcast_ref::<gst_base::BaseSrc>()
                    .unwrap()
                    .set_live(true);
            }
            subclass::Property("recording-location", ..) => {
                let recording_location = value
                    .get()
                    .expect(&format!("k4asrc: Failed to set property `recording-location`. Expected a `string`, but got: {:?}", value));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `recording-location` from {:?} to {:?}",
                    settings.playback_settings.recording_location,
                    recording_location
                );
                settings.playback_settings.recording_location = recording_location;
                obj.downcast_ref::<gst_base::BaseSrc>()
                    .unwrap()
                    .set_live(false);
            }
            subclass::Property("enable-depth", ..) => {
                let enable_depth = value.get().expect(&format!("k4asrc: Failed to set property `enable-depth`. Expected a `bool`, but got: {:?}", value));
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
                let enable_ir = value.get().expect(&format!(
                    "k4asrc: Failed to set property `enable-ir`. Expected a `bool`, but got: {:?}",
                    value
                ));
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
                let enable_color = value.get().expect(&format!("k4asrc: Failed to set property `enable-color`. Expected a `bool`, but got: {:?}", value));
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
                let enable_imu = value.get().expect(&format!(
                    "k4asrc: Failed to set property `enable-imu`. Expected a `bool`, but got: {:?}",
                    value
                ));
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
                let value: i32 = value.get().expect(&format!(
                    "k4asrc: Failed to set property `color-format`. Expected a `i32`, but got: {:?}",
                    value
                ));
                let color_format = image_format_from_i32(value).expect(&format!(
                    "k4asrc: Failed to set property `color-format`. Variant {:?} is not valid.",
                    value
                ));
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
                let value: i32 = value.get().expect(&format!(
                    "k4asrc: Failed to set property `color-resolution`. Expected a `i32`, but got: {:?}",
                    value
                ));
                let color_resolution = color_resolution_from_i32(value).expect(&format!(
                    "k4asrc: Failed to set property `color-resolution`. Variant {:?} is not valid.",
                    value
                ));
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
                let value: i32 = value.get().expect(&format!(
                    "k4asrc: Failed to set property `depth-mode`. Expected a `i32`, but got: {:?}",
                    value
                ));
                let depth_mode = depth_mode_from_i32(value).expect(&format!(
                    "k4asrc: Failed to set property `depth-mode`. Variant {:?} is not valid.",
                    value
                ));
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
                let framerate = value.get().expect(&format!(
                    "k4asrc: Failed to set property `framerate`. Expected a `i32`, but got: {:?}",
                    value
                ));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `framerate` from {} to {}",
                    settings.device_settings.framerate,
                    framerate
                );
                settings.device_settings.framerate = framerate;
            }
            subclass::Property("loop-recording", ..) => {
                let loop_recording = value.get().expect(&format!(
                    "k4asrc: Failed to set property `loop-recording`. Expected a `bool`, but got: {:?}",
                    value
                ));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `loop-recording` from {} to {}",
                    settings.playback_settings.loop_recording,
                    loop_recording
                );
                settings.playback_settings.loop_recording = loop_recording;
            }
            subclass::Property("get-capture-timeout", ..) => {
                let get_capture_timeout = value.get().expect(&format!(
                    "k4asrc: Failed to set property `get-capture-timeout`. Expected a `i32`, but got: {:?}",
                    value
                ));
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `get-capture-timeout` from {} to {}",
                    settings.device_settings.get_capture_timeout,
                    get_capture_timeout
                );
                settings.device_settings.get_capture_timeout = get_capture_timeout;
            }
            subclass::Property("timestamp-mode", ..) => {
                let value: i32 = value.get().expect(&format!(
                    "k4asrc: Failed to set property `timestamp-mode`. Expected a `i32`, but got: {:?}",
                    value
                ));
                // TODO: Ugly and lazy for now, will be substituted with `GEnum` soon
                let timestamp_mode = match value {
                    0 => TimestampMode::Ignore,
                    1 => TimestampMode::Main,
                    2 => TimestampMode::All,
                    3 => TimestampMode::K4aCommon,
                    4 => TimestampMode::K4aIndividual,
                    _ => panic!("k4asrc: Failed to set property `timestamp-mode`. Variant {:?} is not valid.", value)
                };
                element.set_do_timestamp(match timestamp_mode {
                    TimestampMode::Main => true,
                    _ => false,
                });
                gst_info!(
                    CAT,
                    obj: element,
                    "Changing property `timestamp-mode` from {:?} to {:?}",
                    settings.timestamp_mode,
                    timestamp_mode
                );
                settings.timestamp_mode = timestamp_mode;
            }
            _ => unimplemented!("k4asrc: Property is not implemented"),
        };
    }
}

pub fn register(plugin: &gst::Plugin) -> Result<(), glib::BoolError> {
    gst::Element::register(Some(plugin), "k4asrc", gst::Rank::None, K4aSrc::get_type())
}
