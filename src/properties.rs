use crate::settings::*;
use glib::subclass;

/// All properties that `k4asrc` element supports.
pub(crate) static PROPERTIES: [subclass::Property; 14] = [
    subclass::Property("serial", |name| {
        glib::ParamSpec::string(
            name,
            "Serial Number",
            "Serial number of a K4A device. If unchanged or empty, `recording-location` is used to \
             locate a file to play from. If both `serial` and `recording-location` are unchanged or \
             empty, first detected device will be used for streaming.",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("recording-location", |name| {
        glib::ParamSpec::string(
            name,
            "Recording File Location",
            "Location of a recording file to play from. If unchanged or empty, physical device \
             specified by `serial` is used. If both `serial` and `recording-location` are unchanged \
             or empty, first detected device will be used.",
            None,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable-depth", |name| {
        glib::ParamSpec::boolean(
            name,
            "Enable Depth",
            "Enables depth stream.",
            DEFAULT_ENABLE_DEPTH,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable-ir", |name| {
        glib::ParamSpec::boolean(
            name,
            "Enable IR",
            "Enables IR stream. If enabled and `enable-depth` is set to false, the IR resolution \
             is set to 1024x1024 px, otherwise the resolution is determined by `depth-mode` \
             property.",
            DEFAULT_ENABLE_IR,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable-color", |name| {
        glib::ParamSpec::boolean(
            name,
            "Enable Color",
            "Enables color stream.",
            DEFAULT_ENABLE_COLOR,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("enable-imu", |name| {
        glib::ParamSpec::boolean(
            name,
            "Enable IMU",
            "Enables IMU stream.",
            DEFAULT_ENABLE_IMU,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color-format", |name| {
        // TODO: Replace with GEnum
        // Note: It is possible to convert the color format also when streaming from Playback
        // by the use of `k4a_playback_set_color_conversion()` (not tested). However, the decision
        // is to use GStreamer conversion for such purposes instead.
        glib::ParamSpec::int(
            name,
            "Color Format",
            "Format of the color stream, applicable only when streaming from device: \
             \n\t\t\t0 - MJPG \
             \n\t\t\t1 - NV12 (720p only) \
             \n\t\t\t2 - YUY2 (720p only) \
             \n\t\t\t3 - BGRA32 (720p only)",
            k4a::ImageFormat::K4A_IMAGE_FORMAT_COLOR_MJPG as i32,
            k4a::ImageFormat::K4A_IMAGE_FORMAT_COLOR_BGRA32 as i32,
            DEFAULT_COLOR_FORMAT as i32,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color-resolution", |name| {
        // TODO: replace with GEnum
        glib::ParamSpec::int(
            name,
            "Color Resolution",
            "Resolution of the color stream, applicable only when streaming from device: \
             \n\t\t\t1 - 720p \
             \n\t\t\t2 - 1080p \
             \n\t\t\t3 - 1440p \
             \n\t\t\t4 - 1536p \
             \n\t\t\t5 - 2160p \
             \n\t\t\t6 - 3072p",
            k4a::ColorResolution::K4A_COLOR_RESOLUTION_720P as i32,
            k4a::ColorResolution::K4A_COLOR_RESOLUTION_3072P as i32,
            DEFAULT_COLOR_RESOLUTION as i32,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("depth-mode", |name| {
        // TODO: replace with GEnum
        glib::ParamSpec::int(
            name,
            "Depth Mode",
            "Depth capture mode configuration, applicable only when streaming from device: \
             \n\t\t\t1 - NFOV_2x2binned \
             \n\t\t\t2 - NFOV_unbinned \
             \n\t\t\t3 - WFOV_2x2binned \
             \n\t\t\t4 - WFOV_unbinned",
            k4a::DepthMode::K4A_DEPTH_MODE_NFOV_2X2BINNED as i32,
            k4a::DepthMode::K4A_DEPTH_MODE_WFOV_UNBINNED as i32,
            DEFAULT_DEPTH_MODE as i32,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("framerate", |name| {
        // TODO: replace with GEnum
        glib::ParamSpec::int(
            name,
            "Framerate",
            "Common framerate of the selected video streams, applicable only when streaming from device. \
             (30 FPS is not available for `depth-mode=WFOV_unbinned` or `color-resolution=3072p`)",
            ALLOWED_FRAMERATES[0],
            ALLOWED_FRAMERATES[2],
            DEFAULT_FRAMERATE,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("get-capture-timeout", |name| {
        glib::ParamSpec::int(
            name,
            "Get Capture Timeout",
            "Timeout used while waiting for capture from a K4A device in milliseconds. Applicable \
             only when streaming from device",
            1,
            std::i32::MAX,
            DEFAULT_GET_CAPTURE_TIMEOUT,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("loop-recording", |name| {
        glib::ParamSpec::boolean(
            name,
            "Loop recording",
            "Enables looping of playing from recording recording specified by `recording-location` \
             property. This property applies only when streaming from Playback. This property cannot \
             be enabled if `timestamp-mode=k4a_common` or `timestamp-mode=k4a_individual`.",
            DEFAULT_LOOP_RECORDING,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("real-time-playback", |name| {
        glib::ParamSpec::boolean(
            name,
            "Real Time Playback",
            "Determines whether to stream from a recording at the same rate as it was recorded, \
             i.e. pseudo-live source. If set to false, streaming rate will be determined based on \
             the recording rate (and hence the negotiated framerate). If set to false and downstream \
             sink element(s) are set to `async=true`, the streaming rate will be as fast as possible. \
             This property is applicable only when streaming from Playback.",
            DEFAULT_REAL_TIME_PLAYBACK,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("timestamp-mode", |name| {
        // TODO: replace with GEnum
        glib::ParamSpec::int(
            name,
            "Timestamp Mode",
            "Timestamp mode to use: \
             \n\t\t\t0 - ignore: Do not apply timestamp to any buffer \
             \n\t\t\t1 - main: Apply timestamps only to the main buffers based on current stream \
             time (identical to enabling `do-timestamp=true`) \
             \n\t\t\t2 (default) - all: Apply timestamps to all buffers based on current stream \
             time, i.e. since the element was last put to PLAYING \
             \n\t\t\t3 - k4a_common: Apply timestamps to all buffers based on the timestamps obtained \
             from physical K4A device or playback \
             \n\t\t\t4 - k4a_individual: Apply timestamps to all buffers based on the timestamps obtained \
             from physical K4A device or playback",
            TimestampMode::Ignore as i32,
            TimestampMode::K4aIndividual as i32,
            DEFAULT_TIMESTAMP_MODE as i32,
            glib::ParamFlags::READWRITE,
        )
    }),
];
