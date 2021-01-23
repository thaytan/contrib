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

use std::error::Error;
use std::{fmt, fmt::Display, fmt::Formatter};

use super::rgbddemux::CAT;

/// Custom error of `rgbddemux` element
#[derive(Debug, Clone)]
pub struct RgbdDemuxError(pub String);

impl Error for RgbdDemuxError {}

impl Display for RgbdDemuxError {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "RGB-D Demuxing Error: {}", self.0)
    }
}

impl From<RgbdDemuxError> for gst::FlowError {
    fn from(error: RgbdDemuxError) -> Self {
        gst_error!(CAT, "{}", error);
        gst::FlowError::Error
    }
}

impl From<gst::ErrorMessage> for RgbdDemuxError {
    fn from(error: gst::ErrorMessage) -> RgbdDemuxError {
        RgbdDemuxError(format!("{}", error))
    }
}
