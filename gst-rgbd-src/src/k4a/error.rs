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

use libk4a::error::K4aError;
use std::{error, fmt};

/// Enumeration representation of an `K4aError` that can be returned by the `K4aSrc` element.
#[derive(Debug, Clone)]
pub enum K4aSrcError {
    /// `K4aError` that represents all failures.
    Failure(&'static str),
    /// `K4aError` that represents end of file.
    Eof,
}
impl error::Error for K4aSrcError {}
impl fmt::Display for K4aSrcError {
    fn fmt(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
        use K4aSrcError::*;
        match self {
            Failure(err_msg) => write!(formatter, "Failure: {}!", err_msg),
            Eof => write!(formatter, "End of File/Stream!"),
        }
    }
}

/// Conversion from `K4aError` (k4a-rs) to `K4aSrcError` (gst-realsense), which useful for
/// the ? operator in multiple functions that interface with the rust bindings.
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

/// Conversion from `K4aSrcError` to gst::ErrorMessage, which useful in `start()` and `stop()`
/// virtual methods for the ? operator.
impl From<K4aSrcError> for gst::ErrorMessage {
    fn from(error: K4aSrcError) -> gst::ErrorMessage {
        gst::error_msg!(gst::ResourceError::Failed, ["{}", error])
    }
}

/// Conversion from `K4aSrcError` to gst::FlowError, which useful in `create()` virtual method
/// for the ? operator.
impl From<K4aSrcError> for gst::FlowError {
    fn from(error: K4aSrcError) -> gst::FlowError {
        use K4aSrcError::*;
        match error {
            Failure(err_msg) => {
                // Print the specific error to STDERR as there is no way of passing it to gst::FlowError.
                eprintln!("k4asrc: Returning gst::FlowError - {}", err_msg);
                gst::FlowError::Error
            }
            Eof => gst::FlowError::Eos,
        }
    }
}

/// Conversion from `gst::ErrorMessage` to K4aSrcError.
impl From<gst::ErrorMessage> for K4aSrcError {
    fn from(error: gst::ErrorMessage) -> K4aSrcError {
        K4aSrcError::Failure(std::boxed::Box::leak(format!("{}", error).into_boxed_str()))
    }
}
