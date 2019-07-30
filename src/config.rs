use crate::error::Error;
use rs2;

#[derive(Debug)]
pub struct Config {
    pub raw: *mut rs2::rs2_config,
}

unsafe impl Send for Config {}

unsafe impl Sync for Config {}

impl Drop for Config {
    fn drop(&mut self) {
        unsafe {
            rs2::rs2_delete_config(self.raw);
        }
    }
}

impl Config {
    pub fn new() -> Result<Config, Error> {
        let mut error = Error::default();
        let config = Config {
            raw: unsafe { rs2::rs2_create_config(error.inner()) },
        };
        if error.check() {
            Err(error)
        } else {
            Ok(config)
        }
    }

    pub fn enable_device(&self, serial: String) -> Result<(), Error> {
        let mut error = Error::default();
        let s = std::ffi::CString::new(serial).expect("Failed to create CString");
        unsafe {
            rs2::rs2_config_enable_device(self.raw, s.as_ptr(), error.inner());
        }
        std::mem::forget(s);
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    pub fn enable_device_from_file(&self, file: String) -> Result<(), Error> {
        let mut error = Error::default();
        let s = std::ffi::CString::new(file).expect("Failed to create CString");
        unsafe {
            rs2::rs2_config_enable_device_from_file(self.raw, s.as_ptr(), error.inner());
        }
        std::mem::forget(s);
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    pub fn enable_device_from_file_repeat_option(
        &self,
        file: String,
        repeat: bool,
    ) -> Result<(), Error> {
        let mut error = Error::default();
        let s = std::ffi::CString::new(file).expect("Failed to create CString");
        unsafe {
            rs2::rs2_config_enable_device_from_file_repeat_option(
                self.raw,
                s.as_ptr(),
                repeat as i32,
                error.inner(),
            );
        }
        std::mem::forget(s);
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    pub fn enable_stream(
        &self,
        stream: rs2::rs2_stream,
        index: i32,
        width: i32,
        height: i32,
        format: rs2::rs2_format,
        framerate: i32,
    ) -> Result<(), Error> {
        let mut error = Error::default();
        unsafe {
            rs2::rs2_config_enable_stream(
                self.raw,
                stream,
                index,
                width,
                height,
                format,
                framerate,
                error.inner(),
            );
        }
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    pub fn enable_record_to_file(&self, file: String) -> Result<(), Error> {
        let mut error = Error::default();
        let s = std::ffi::CString::new(file).expect("Failed to create CString");
        unsafe {
            rs2::rs2_config_enable_record_to_file(self.raw, s.as_ptr(), error.inner());
        }
        std::mem::forget(s);
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }
}
