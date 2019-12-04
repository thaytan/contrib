use crate::settings::*;

// Unique identifiers of streams
/// ID of the depth stream.
pub(crate) const STREAM_ID_DEPTH: &str = "depth";
/// ID of the IR stream.
pub(crate) const STREAM_ID_IR: &str = "ir";
/// ID of the color stream.
pub(crate) const STREAM_ID_COLOR: &str = "color";
/// ID of the IMU stream.
pub(crate) const STREAM_ID_IMU: &str = "imu";

/// A struct containing information about what streams are enabled.
#[derive(Clone, Copy)]
pub(crate) struct Streams {
    /// Determines whether depth stream is enabled.
    pub(crate) depth: bool,
    /// Determines whether IR stream is enabled.
    pub(crate) ir: bool,
    /// Determines whether color stream is enabled.
    pub(crate) color: bool,
    /// Determines whether IMU stream is enabled.
    pub(crate) imu: bool,
}

impl Default for Streams {
    fn default() -> Self {
        Self {
            depth: DEFAULT_ENABLE_DEPTH,
            ir: DEFAULT_ENABLE_IR,
            color: DEFAULT_ENABLE_COLOR,
            imu: DEFAULT_ENABLE_IMU,
        }
    }
}

impl Streams {
    /// Determine whether at least one stream is enabled. Includes IMU stream.
    ///
    /// # Returns
    /// * `true` if at least one stream is enabled.
    /// * `false` if no stream is enabled.
    pub(crate) fn is_any_enabled(&self) -> bool {
        self.depth | self.ir | self.color | self.imu
    }

    /// Determine whether at least one video stream is enabled. IMU stream is ignored.
    ///
    /// # Returns
    /// * `true` if at least one video stream is enabled.
    /// * `false` if no stream is enabled.
    pub(crate) fn is_any_video_enabled(&self) -> bool {
        self.depth | self.ir | self.color
    }

    /// Determine whether there are any conflict between `enabled_streams` and
    /// `available_streams`
    ///
    /// # Arguments
    /// * `enabled_streams` - The streams that are enabled.
    /// * `available_streams` - The streams that are available.
    ///
    /// # Returns
    /// * `Vec<&str>` of conflicting streams, which is empty if there is no conflict.
    pub(crate) fn are_streams_available(
        enabled_streams: &Streams,
        available_streams: &Streams,
    ) -> bool {
        !((enabled_streams.depth && !available_streams.depth)
            || (enabled_streams.ir && !available_streams.ir)
            || (enabled_streams.color && !available_streams.color)
            || (enabled_streams.imu && !available_streams.imu))
    }
}
