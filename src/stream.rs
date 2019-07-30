use crate::error::Error;

pub struct StreamData {
    pub stream: rs2::rs2_stream,
    pub format: rs2::rs2_format,
    pub index: i32,
    pub id: i32,
    pub framerate: i32,
}

#[derive(Debug)]
pub struct StreamProfile {
    pub raw: *mut rs2::rs2_stream_profile,
    pub clone: bool,
}

unsafe impl Send for StreamProfile {}

unsafe impl Sync for StreamProfile {}

impl Drop for StreamProfile {
    fn drop(&mut self) {
        if self.clone {
            unsafe {
                rs2::rs2_delete_stream_profile(self.raw);
            }
        }
    }
}

impl StreamProfile {
    pub fn get_data(&self) -> Result<StreamData, Error> {
        let mut error = Error::default();
        let mut data = StreamData {
            stream: rs2::rs2_stream::RS2_STREAM_ANY,
            format: rs2::rs2_format::RS2_FORMAT_ANY,
            index: 0,
            id: 0,
            framerate: 0,
        };
        unsafe {
            rs2::rs2_get_stream_profile_data(
                self.raw,
                &mut data.stream as *mut rs2::rs2_stream,
                &mut data.format as *mut rs2::rs2_format,
                &mut data.index as *mut i32,
                &mut data.id as *mut i32,
                &mut data.framerate as *mut i32,
                error.inner(),
            );
        }
        if error.check() {
            Err(error)
        } else {
            Ok(data)
        }
    }

    pub fn get_resolution(&self) -> Result<(i32, i32), Error> {
        let mut error = Error::default();
        let mut res: (i32, i32) = (0, 0);
        unsafe {
            rs2::rs2_get_video_stream_resolution(
                self.raw,
                &mut res.0 as *mut i32,
                &mut res.1 as *mut i32,
                error.inner(),
            );
        }
        if error.check() {
            Err(error)
        } else {
            Ok(res)
        }
    }
}
