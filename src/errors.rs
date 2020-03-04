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

/// Conversion from `gst::ErrorMessage` to RealsenseError.
impl From<gst::ErrorMessage> for RealsenseError {
    fn from(error: gst::ErrorMessage) -> RealsenseError {
        RealsenseError(format!("{}", error))
    }
}
