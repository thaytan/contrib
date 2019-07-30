use crate::device::Device;
use crate::error::Error;
use rs2;

#[derive(Debug)]
pub struct Context {
    pub raw: *mut rs2::rs2_context,
}

unsafe impl Send for Context {}

unsafe impl Sync for Context {}

impl Drop for Context {
    fn drop(&mut self) {
        unsafe {
            rs2::rs2_delete_context(self.raw);
        }
    }
}

impl Context {
    pub fn new() -> Result<Context, Error> {
        let mut error = Error::default();
        let api_version: i32 = rs2::RS2_API_VERSION as i32;
        let context = Context {
            raw: unsafe { rs2::rs2_create_context(api_version, error.inner()) },
        };
        if error.check() {
            Err(error)
        } else {
            Ok(context)
        }
    }

    pub fn get_devices(&self) -> Result<Vec<Device>, Error> {
        let mut error = Error::default();
        let device_list = unsafe { rs2::rs2_query_devices(self.raw, error.inner()) };
        if error.check() {
            return Err(error);
        };

        let count = unsafe { rs2::rs2_get_device_count(device_list, error.inner()) };
        let mut res: Vec<Device> = Vec::new();
        for i in 0..count {
            res.push(Device {
                raw: unsafe { rs2::rs2_create_device(device_list, i, error.inner()) },
            });
            if error.check() {
                return Err(error);
            };
        }
        Ok(res)
    }
}
