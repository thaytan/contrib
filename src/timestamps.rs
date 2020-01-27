/// A struct that contains data associated with timestamps and frame duration.
pub(crate) struct TimestampInternals {
    /// Contains frame duration based on framerate.
    pub(crate) frame_duration: gst::ClockTime,
    /// Contains common timestamp for one capture.
    /// Applicable only for `TimestampMode::All` and `TimestampMode::K4aCommon`.
    pub(crate) common_timestamp: gst::ClockTime,
    /// Contains timestamp of the first acquired frame.
    /// Applicable only for `TimestampMode::K4aCommon` and `TimestampMode::K4aIndividual`.
    pub(crate) first_frame_timestamp: gst::ClockTime,
}

/// An enum that countains source of the timestamp, either Image or ImuSample.
pub(crate) enum TimestampSource<'a> {
    Image(&'a k4a::image::Image),
    ImuSample(&'a k4a::imu_sample::ImuSample),
}

impl<'a> TimestampSource<'a> {
    /// Extract timestamp either from `Image` or `ImuSample`
    ///
    /// # Returns
    /// * `gst::ClockTime` containing the timestamp.
    pub(crate) fn extract_timestamp(&self) -> gst::ClockTime {
        match self {
            TimestampSource::Image(image) => gst::ClockTime::from_useconds(image.get_timestamp()),
            TimestampSource::ImuSample(imu_sample) => {
                gst::ClockTime::from_useconds(imu_sample.get_acc_timestamp())
            }
        }
    }
}
