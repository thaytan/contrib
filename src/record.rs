use libk4a_sys::*;

/// Struct representation [`Record`](../record/struct.Record.html) that wraps around `k4a_record_t`,
/// which is a handle to a recording opened for record.
pub struct Record {
    pub(crate) handle: k4a_record_t,
}

/// Safe releasing of the `k4a_record_t` handle.
impl Drop for Record {
    fn drop(&mut self) {
        unsafe {
            k4a_record_close(self.handle);
        }
    }
}

impl Record {
    /// This function is NOT implemented!
    pub fn create(&self) {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn add_tag(&self) {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn add_imu_track(&self) {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn write_header(&self) {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn write_capture(&self) {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn write_imu_sample(&self) {
        unimplemented!()
    }

    /// This function is NOT implemented!
    pub fn flush(&self) {
        unimplemented!()
    }
}
