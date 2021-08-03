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

use glib::*;
use gst::*;

pub trait ToErrorMessage {
    /// Converts `self` to a gstreamer `ErrorMessage` in `domain`.
    fn to_err_msg<Err: MessageErrorDomain>(&self, domain: Err) -> ErrorMessage;
}

impl ToErrorMessage for BoolError {
    fn to_err_msg<Err: MessageErrorDomain>(&self, domain: Err) -> ErrorMessage {
        ErrorMessage::new(
            &domain,
            Some(&self.message),
            None,
            self.filename,
            self.function,
            self.line,
        )
    }
}

pub trait MapErrorMessage<Out> {
    /// Maps result error to gstreamer error message
    fn map_err_msg<Err: MessageErrorDomain>(self, domain: Err) -> Result<Out, ErrorMessage>;
}

impl<T, E> MapErrorMessage<T> for Result<T, E>
where
    E: ToErrorMessage,
{
    fn map_err_msg<Err: MessageErrorDomain>(self, domain: Err) -> Result<T, ErrorMessage> {
        self.map_err(|e| e.to_err_msg(domain))
    }
}
