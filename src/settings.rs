pub(crate) use crate::enabled_streams::EnabledStreams;
pub(crate) use crate::properties_d435::*;
pub(crate) use rs2::stream_profile::StreamResolution;

// Default behaviour of playing from rosbag recording specified by `rosbag-location` property.
pub(crate) const DEFAULT_LOOP_ROSBAG: bool = true;
// Default timeout used while waiting for frames from a realsense device in milliseconds.
pub(crate) const DEFAULT_PIPELINE_WAIT_FOR_FRAMES_TIMEOUT: u32 = 2500;
// Default behaviour for enablind metadata
pub(crate) const DEFAULT_ENABLE_METADATA: bool = false;
// Default behaviour for adding custom timestamps to the buffers.
pub(crate) const DEFAULT_DO_CUSTOM_TIMESTAMP: bool = true;

/// A struct containing properties of `realsensesrc`
pub(crate) struct Settings {
    pub(crate) serial: Option<String>,
    pub(crate) rosbag_location: Option<String>,
    pub(crate) json_location: Option<String>,
    pub(crate) streams: Streams,
    pub(crate) loop_rosbag: bool,
    pub(crate) wait_for_frames_timeout: u32,
    pub(crate) include_per_frame_metadata: bool,
    pub(crate) do_custom_timestamp: bool,
}

pub(crate) struct Streams {
    pub(crate) enabled_streams: EnabledStreams,
    pub(crate) depth_resolution: StreamResolution,
    pub(crate) color_resolution: StreamResolution,
    pub(crate) framerate: i32,
}

impl Default for Settings {
    fn default() -> Self {
        Settings {
            rosbag_location: None,
            serial: None,
            json_location: None,
            streams: Streams {
                enabled_streams: EnabledStreams {
                    depth: DEFAULT_ENABLE_DEPTH,
                    infra1: DEFAULT_ENABLE_INFRA1,
                    infra2: DEFAULT_ENABLE_INFRA2,
                    color: DEFAULT_ENABLE_COLOR,
                },
                depth_resolution: StreamResolution {
                    width: DEFAULT_DEPTH_WIDTH,
                    height: DEFAULT_DEPTH_HEIGHT,
                },
                color_resolution: StreamResolution {
                    width: DEFAULT_COLOR_WIDTH,
                    height: DEFAULT_COLOR_HEIGHT,
                },
                framerate: DEFAULT_FRAMERATE,
            },
            loop_rosbag: DEFAULT_LOOP_ROSBAG,
            wait_for_frames_timeout: DEFAULT_PIPELINE_WAIT_FOR_FRAMES_TIMEOUT,
            include_per_frame_metadata: DEFAULT_ENABLE_METADATA,
            do_custom_timestamp: DEFAULT_DO_CUSTOM_TIMESTAMP,
        }
    }
}
