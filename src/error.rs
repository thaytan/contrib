// License: MIT. See LICENSE file in root directory.
// Copyright(c) 2019 Aivero. All Rights Reserved.
use crate::low_level_utils::cstring_to_string;
use rs2;
use std::{error, fmt};

/// Struct representation of an [`Error`](../error/struct.Error.html) that wraps around
/// `rs2_error` handle.
#[derive(Debug)]
pub struct Error {
    pub(crate) handle: *mut rs2::rs2_error,
}

/// Safe releasing of the `rs2_error` handle.
impl Drop for Error {
    fn drop(&mut self) {
        unsafe {
            rs2::rs2_free_error(self.handle);
        }
    }
}

/// Default constructor of [`Error`](../error/struct.Error.html) that contains no error.
impl Default for Error {
    fn default() -> Self {
        Self {
            handle: std::ptr::null_mut::<rs2::rs2_error>(),
        }
    }
}

/// Define the source of [`Error`](../error/struct.Error.html).
impl error::Error for Error {
    fn description(&self) -> &str {
        "RealSense Error"
    }
}

/// Formatting of [`Error`](../error/struct.Error.html).
impl fmt::Display for Error {
    fn fmt(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
        formatter.write_str(self.get_message().as_str())
    }
}

impl Error {
    /// Return `*mut *mut rs2::rs2_error` handle required by other functions of the API.
    pub(crate) fn inner(&mut self) -> *mut *mut rs2::rs2_error {
        &mut self.handle as *mut *mut rs2::rs2_error
    }

    /// Check the value of [`Error`](../error/struct.Error.html).
    ///
    /// # Returns
    /// * `bool` that returs `true` if the struct [`Error`](../error/struct.Error.html)
    /// contains an error
    /// that occured and
    /// false if everything went fine.
    pub fn check(&self) -> bool {
        !self.handle.is_null()
    }

    /// Return the message of the error.
    pub fn get_message(&self) -> String {
        unsafe { cstring_to_string(rs2::rs2_get_error_message(self.handle)) }
    }

    /// Return the function in which the error occured.
    pub fn get_function(&self) -> String {
        unsafe { cstring_to_string(rs2::rs2_get_failed_function(self.handle)) }
    }

    /// Return what arguments caused the error.
    pub fn get_args(&self) -> String {
        unsafe { cstring_to_string(rs2::rs2_get_failed_args(self.handle)) }
    }
}
