use k4a::error::K4aError;
use std::{error, fmt};

/// Enumeration representation of an `K4aError` that can be returned by using this library.
#[derive(Debug, Clone)]
pub enum K4aSrcError {
    /// `K4aError` that represents all failures.
    Failure(&'static str),
    /// `K4aError` that represents end of file.
    Eof,
}

impl error::Error for K4aSrcError {
    fn description(&self) -> &str {
        "K4A Source Error"
    }
    fn source(&self) -> Option<&(dyn error::Error + 'static)> {
        use K4aSrcError::*;
        match self {
            Failure(_) => Some(self),
            Eof => None,
        }
    }
}

impl fmt::Display for K4aSrcError {
    fn fmt(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
        use K4aSrcError::*;
        match self {
            Failure(err_msg) => write!(formatter, "Failure: {}!", err_msg),
            Eof => write!(formatter, "End of File/Stream!"),
        }
    }
}

impl From<K4aError> for K4aSrcError {
    fn from(error: K4aError) -> K4aSrcError {
        use K4aError::*;
        match error {
            Failure(err_msg) => K4aSrcError::Failure(err_msg),
            Timeout => K4aSrcError::Failure("Timed Out!"),
            Eof => K4aSrcError::Eof,
        }
    }
}

impl From<K4aSrcError> for gst::ErrorMessage {
    fn from(error: K4aSrcError) -> gst::ErrorMessage {
        gst_error_msg!(gst::ResourceError::Failed, ["{}", error])
    }
}

impl From<K4aSrcError> for gst::FlowError {
    fn from(error: K4aSrcError) -> gst::FlowError {
        use K4aSrcError::*;
        match error {
            Failure(err_msg) => {
                println!("k4asrc: Returning gst::FlowError - {}", err_msg);
                gst::FlowError::Error
            }
            Eof => gst::FlowError::Eos,
        }
    }
}
