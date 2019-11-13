use std::error::Error;
use std::fmt;
use std::fmt::{Display, Formatter};

#[derive(Clone, Debug)]
pub(crate) struct RealsenseError(pub(crate) String);

impl Error for RealsenseError {}

impl Display for RealsenseError {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "Could not enable stream: {}", self.0)
    }
}

impl From<rs2::error::Error> for RealsenseError {
    fn from(error: rs2::error::Error) -> Self {
        Self(error.get_message())
    }
}

impl From<RealsenseError> for gst::FlowError {
    fn from(e: RealsenseError) -> Self {
        gst_error!(
            gst::DebugCategory::new(
                "realsensesrc",
                gst::DebugColorFlags::empty(),
                Some("Realsense Source"),
            ),
            "{}",
            e
        );
        gst::FlowError::Error
    }
}

#[derive(Clone, Debug)]
pub(crate) struct StreamEnableError(pub(crate) &'static str);

impl Error for StreamEnableError {}

impl Display for StreamEnableError {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "Could not enable stream: {}", self.0)
    }
}
