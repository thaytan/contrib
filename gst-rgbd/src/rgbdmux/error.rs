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

/// Custom error of `rgbdmux` element
#[derive(Debug, Clone)]
pub struct RgbdMuxError(pub String);

impl Error for RgbdMuxError {}

impl Display for RgbdMuxError {
    fn fmt(&self, f: &mut Formatter) -> fmt::Result {
        write!(f, "RGB-D Muxing Error: {}", self.0)
    }
}

impl From<gst::ErrorMessage> for RgbdMuxError {
    fn from(error: gst::ErrorMessage) -> RgbdMuxError {
        RgbdMuxError(format!("{}", error))
    }
}
