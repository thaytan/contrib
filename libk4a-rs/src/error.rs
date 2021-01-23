use std::{error, fmt};

/// Type of Result used in this library.
pub(crate) type Result<T> = std::result::Result<T, K4aError>;

/// Enumeration representation of an `K4aError` that can be returned by using this library.
#[derive(Debug, Clone)]
pub enum K4aError {
    /// `K4aError` that represents all failures.
    Failure(&'static str),
    /// `K4aError` that represents function timeout.
    Timeout,
    /// `K4aError` that represents end of file.
    Eof,
}

impl error::Error for K4aError {}

impl fmt::Display for K4aError {
    fn fmt(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
        use K4aError::*;
        match self {
            Failure(ref err_msg) => write!(formatter, "Failure: {}!", err_msg),
            Timeout => write!(formatter, "Timed Out!"),
            Eof => write!(formatter, "End of File/Stream!"),
        }
    }
}
