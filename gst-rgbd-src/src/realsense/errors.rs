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

use std::error::Error;
use std::fmt;
use std::fmt::{Display, Formatter};

use super::realsensesrc::CAT;
use super::settings::StreamsSettings;

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

impl From<RealsenseError> for gst::ErrorMessage {
    fn from(e: RealsenseError) -> Self {
        gst_error!(CAT, "{}", e);
        gst_error_msg!(gst::StreamError::Failed, (&e.0))
    }
}

impl From<RealsenseError> for gst::FlowError {
    fn from(e: RealsenseError) -> Self {
        gst_error!(CAT, "{}", e);
        gst::FlowError::Error
    }
}

#[derive(Clone, Debug)]
pub(crate) struct StreamEnableError(pub(crate) String);

impl Error for StreamEnableError {}

impl Display for StreamEnableError {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "Could not enable stream: {}", self.0)
    }
}

impl From<StreamEnableError> for RealsenseError {
    fn from(error: StreamEnableError) -> Self {
        Self(error.0)
    }
}

/// Conversion from `gst::ErrorMessage` to RealsenseError.
impl From<gst::ErrorMessage> for RealsenseError {
    fn from(error: gst::ErrorMessage) -> RealsenseError {
        RealsenseError(format!("{}", error))
    }
}

/// ConfigError occurs when a `librealsense2` pipeline config cannot be resolved, which is used to provide more
/// descriptive error messages to the user.
#[derive(Debug, Clone, PartialEq)]
pub(crate) enum ConfigError {
    /// Error that occurs when a physical RealSense device cannot be opened for streaming.
    DeviceNotFound(String),
    /// Error that occurs in case the combination of resolution and framerate is invalid for the connected device
    /// with a specific firmware.
    InvalidRequest(StreamsSettings),
    /// Other errors that either do not need more detailed error handling, or they occur only rarely.
    Other(String),
}

impl std::error::Error for ConfigError {}
impl std::fmt::Display for ConfigError {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            ConfigError::DeviceNotFound(serial) => {
                write!(f, "Device with serial '{}' is not connected", serial)
            }
            ConfigError::InvalidRequest(streams) => write!(
                f,
                "The selected RealSense configuration is NOT supported by your device: {}",
                streams
            ),
            ConfigError::Other(err_msg) => write!(
                f,
                "Failed to prepare and start librealsense2 pipeline: {}",
                err_msg
            ),
        }
    }
}

impl From<ConfigError> for RealsenseError {
    fn from(error: ConfigError) -> Self {
        Self(error.to_string())
    }
}
