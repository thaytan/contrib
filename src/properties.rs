use crate::settings::*;
use glib::subclass;

/// All properties that `k4asrc` element supports.
pub(crate) static PROPERTIES: [subclass::Property; 13] = [
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
        glib::ParamSpec::int(
            name,
            "Color Format",
            "Format of the color stream: \
             \n\t\t\t0 - K4A_IMAGE_FORMAT_COLOR_MJPG \
             \n\t\t\t1 - K4A_IMAGE_FORMAT_COLOR_NV12 \
             \n\t\t\t2 - K4A_IMAGE_FORMAT_COLOR_YUY2 \
             \n\t\t\t3 - K4A_IMAGE_FORMAT_COLOR_BGRA32",
            k4a::ImageFormat::K4A_IMAGE_FORMAT_COLOR_MJPG as i32,
            k4a::ImageFormat::K4A_IMAGE_FORMAT_COLOR_BGRA32 as i32,
            DEFAULT_COLOR_FORMAT as i32,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("color-resolution", |name| {
        glib::ParamSpec::int(
            name,
            "Color Resolution",
            "Resolution of the color stream: \
             \n\t\t\t1 - K4A_COLOR_RESOLUTION_720P \
             \n\t\t\t2 - K4A_COLOR_RESOLUTION_1080P \
             \n\t\t\t3 - K4A_COLOR_RESOLUTION_1440P \
             \n\t\t\t4 - K4A_COLOR_RESOLUTION_1536P \
             \n\t\t\t5 - K4A_COLOR_RESOLUTION_2160P \
             \n\t\t\t6 - K4A_COLOR_RESOLUTION_3072P",
            k4a::ColorResolution::K4A_COLOR_RESOLUTION_720P as i32,
            k4a::ColorResolution::K4A_COLOR_RESOLUTION_3072P as i32,
            DEFAULT_COLOR_RESOLUTION as i32,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("depth-mode", |name| {
        glib::ParamSpec::int(
            name,
            "Depth Mode",
            "Depth capture mode configuration: \
             \n\t\t\t1 - K4A_DEPTH_MODE_NFOV_2X2BINNED \
             \n\t\t\t2 - K4A_DEPTH_MODE_NFOV_UNBINNED \
             \n\t\t\t3 - K4A_DEPTH_MODE_WFOV_2X2BINNED \
             \n\t\t\t4 - K4A_DEPTH_MODE_WFOV_UNBINNED",
            k4a::DepthMode::K4A_DEPTH_MODE_NFOV_2X2BINNED as i32,
            k4a::DepthMode::K4A_DEPTH_MODE_WFOV_UNBINNED as i32,
            DEFAULT_DEPTH_MODE as i32,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("framerate", |name| {
        glib::ParamSpec::int(
            name,
            "Framerate",
            "Common framerate of the selected video streams.",
            ALLOWED_FRAMERATES[0],
            ALLOWED_FRAMERATES[2],
            DEFAULT_FRAMERATE,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("loop-recording", |name| {
        glib::ParamSpec::boolean(
            name,
            "Loop recording",
            "Enables looping of playing from recording recording specified by `recording-location` \
            property. This property applies only if streaming from playback. This property cannot \
            be enabled if `do-k4a-timestamp` property is set to true.",
            DEFAULT_LOOP_RECORDING,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("get-capture-timeout", |name| {
        glib::ParamSpec::int(
            name,
            "Wait For Frames Timeout",
            "Timeout used while waiting for frames from a K4A device in milliseconds. This \
             property applies only if streaming from device.",
            1,
            std::i32::MAX,
            DEFAULT_GET_CAPTURE_TIMEOUT,
            glib::ParamFlags::READWRITE,
        )
    }),
    subclass::Property("do-k4a-timestamp", |name| {
        glib::ParamSpec::boolean(
            name,
            "Perform custom timestamp handling",
            "Adds timestamps to all buffers based on the duration since the element was created. \
             As oppose to `do-timestamp`, this property adds the timestamps to all meta Buffers. \
             This property cannot be enabled if streaming from playback and `loop-recording` \
             property is set to true.",
            DEFAULT_DO_K4A_TIMESTAMP,
            glib::ParamFlags::READWRITE,
        )
    }),
];
