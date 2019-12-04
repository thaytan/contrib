use crate::streams::*;
use k4a::{ColorResolution, DepthMode, ImageFormat};

// Streams enabled by default
/// Determines whether streaming depth frames is enabled by default.
pub(crate) const DEFAULT_ENABLE_DEPTH: bool = true;
/// Determines whether streaming IR frames is enabled by default.
pub(crate) const DEFAULT_ENABLE_IR: bool = false;
/// Determines whether streaming color frames is enabled by default.
pub(crate) const DEFAULT_ENABLE_COLOR: bool = false;
/// Determines whether streaming IMU measurements is enabled by default.
pub(crate) const DEFAULT_ENABLE_IMU: bool = false;

// Default settings for K4A specifics
/// The format utilised for streaming depth frames from K4A device.
pub(crate) const DEPTH_FORMAT: ImageFormat = ImageFormat::K4A_IMAGE_FORMAT_DEPTH16;
/// The format utilised for streaming IR frames from K4A device.
pub(crate) const IR_FORMAT: ImageFormat = ImageFormat::K4A_IMAGE_FORMAT_IR16;
/// Default color format for streaming from K4A device.
pub(crate) const DEFAULT_COLOR_FORMAT: ImageFormat = ImageFormat::K4A_IMAGE_FORMAT_COLOR_NV12;
/// Default color resolution for streming from K4A device.
pub(crate) const DEFAULT_COLOR_RESOLUTION: ColorResolution =
    ColorResolution::K4A_COLOR_RESOLUTION_720P;
/// Default depth mode for streming from K4A device.
pub(crate) const DEFAULT_DEPTH_MODE: DepthMode = DepthMode::K4A_DEPTH_MODE_WFOV_UNBINNED;

// Framerates
/// All allowed framerates for streaming video.
pub(crate) const ALLOWED_FRAMERATES: [i32; 3] = [5, 15, 30];
/// The rate at which IMU outputs its measurements.
pub(crate) const IMU_SAMPLING_RATE_HZ: i32 = 208;
/// Default framerate for streaming video from K4A device.
pub(crate) const DEFAULT_FRAMERATE: i32 = ALLOWED_FRAMERATES[1];

// Default settings for GStreamer specifics
/// Default timeout duration while waiting for frames when streaming from K4A device.
pub(crate) const DEFAULT_GET_CAPTURE_TIMEOUT: i32 = 500;
/// Default behaviour of looping playback from recording.
pub(crate) const DEFAULT_LOOP_RECORDING: bool = false;
/// Default behaviour for applying custom timestamps to all buffers.
pub(crate) const DEFAULT_DO_K4A_TIMESTAMP: bool = true;

// TODO: If desired, make these into properties with the appropriate support
pub(crate) const DEPTH_DELAY_OFF_COLOR_USEC: i32 = 0;
pub(crate) const WIRED_SYNCH_MODE: k4a::WiredSyncMode =
    k4a::WiredSyncMode::K4A_WIRED_SYNC_MODE_STANDALONE;
pub(crate) const SUBORDINATE_DELAY_OFF_MASTER_USEC: u32 = 0;
pub(crate) const DISABLE_STREAMING_INDICATOR: bool = false;

/// A struct containing properties.
pub(crate) struct Settings {
    pub(crate) device_settings: DeviceSettings,
    pub(crate) playback_settings: PlaybackSettings,
    pub(crate) desired_streams: Streams,
    pub(crate) do_k4a_timestamp: bool,
}

/// A struct containing properties specific for streaming from a physical K4A device.
pub(crate) struct DeviceSettings {
    pub(crate) serial: String,
    pub(crate) color_format: ImageFormat,
    pub(crate) color_resolution: ColorResolution,
    pub(crate) depth_mode: DepthMode,
    pub(crate) framerate: i32,
    pub(crate) get_capture_timeout: i32,
}

/// A struct containing properties specific for streaming playback from a recording.
pub(crate) struct PlaybackSettings {
    pub(crate) recording_location: String,
    pub(crate) loop_recording: bool,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            device_settings: DeviceSettings {
                serial: String::default(),
                color_format: DEFAULT_COLOR_FORMAT,
                color_resolution: DEFAULT_COLOR_RESOLUTION,
                depth_mode: DEFAULT_DEPTH_MODE,
                framerate: DEFAULT_FRAMERATE,
                get_capture_timeout: DEFAULT_GET_CAPTURE_TIMEOUT,
            },
            desired_streams: Streams::default(),
            playback_settings: PlaybackSettings {
                recording_location: String::default(),
                loop_recording: DEFAULT_LOOP_RECORDING,
            },
            do_k4a_timestamp: DEFAULT_DO_K4A_TIMESTAMP,
        }
    }
}
