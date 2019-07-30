use crate::util::to_string;
use rs2;
use std::error;
use std::fmt;

#[derive(Debug)]
pub struct Error {
    raw: *mut rs2::rs2_error,
    message: Option<String>,
}

impl Default for Error {
    fn default() -> Self {
        Self {
            raw: 0 as *mut rs2::rs2_error,
            message: None,
        }
    }
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.write_str(self.get_message().as_str())
    }
}

impl error::Error for Error {
    fn description(&self) -> &str {
        "Realsense Error"
    }
}

impl Drop for Error {
    fn drop(&mut self) {
        unsafe {
            rs2::rs2_free_error(self.raw);
        }
    }
}

impl Error {
    pub fn new(message: &str) -> Error {
        Error {
            raw: 0 as *mut rs2::rs2_error,
            message: Some(message.to_string()),
        }
    }

    pub fn inner(&mut self) -> *mut *mut rs2::rs2_error {
        &mut self.raw as *mut *mut rs2::rs2_error
    }

    pub fn check(&self) -> bool {
        return self.message != None || !self.raw.is_null();
    }

    pub fn get_message(&self) -> String {
        unsafe {
            if let Some(message) = &self.message {
                message.clone()
            } else {
                to_string(rs2::rs2_get_error_message(self.raw))
            }
        }
    }

    pub fn get_function(&self) -> String {
        unsafe { to_string(rs2::rs2_get_failed_function(self.raw)) }
    }

    pub fn get_args(&self) -> String {
        unsafe { to_string(rs2::rs2_get_failed_args(self.raw)) }
    }
}
