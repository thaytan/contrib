use crate::device::Device;
use crate::error::Error;
use crate::frame::Frame;
use crate::stream::StreamProfile;
use rs2;

#[derive(Debug)]
pub struct Pipeline {
    raw: *mut rs2::rs2_pipeline,
}

#[derive(Debug)]
pub struct PipelineProfile {
    raw: *mut rs2::rs2_pipeline_profile,
}

unsafe impl Send for Pipeline {}

unsafe impl Sync for Pipeline {}

unsafe impl Send for PipelineProfile {}

unsafe impl Sync for PipelineProfile {}

impl Drop for Pipeline {
    fn drop(&mut self) {
        unsafe {
            rs2::rs2_delete_pipeline(self.raw);
        }
    }
}

impl Drop for PipelineProfile {
    fn drop(&mut self) {
        unsafe {
            rs2::rs2_delete_pipeline_profile(self.raw);
        }
    }
}

impl Pipeline {
    pub fn new(ctx: &crate::context::Context) -> Result<Pipeline, Error> {
        let mut error = Error::default();
        let pipeline = Pipeline {
            raw: unsafe { rs2::rs2_create_pipeline(ctx.raw, error.inner()) },
        };
        if error.check() {
            Err(error)
        } else {
            Ok(pipeline)
        }
    }

    pub fn start(&self) -> Result<PipelineProfile, Error> {
        let mut error = Error::default();
        let profile = PipelineProfile {
            raw: unsafe { rs2::rs2_pipeline_start(self.raw, error.inner()) },
        };
        if error.check() {
            Err(error)
        } else {
            Ok(profile)
        }
    }

    pub fn start_with_config(
        &self,
        rs2_config: &crate::config::Config,
    ) -> Result<PipelineProfile, Error> {
        let mut error = Error::default();
        let profile = PipelineProfile {
            raw: unsafe {
                rs2::rs2_pipeline_start_with_config(self.raw, rs2_config.raw, error.inner())
            },
        };
        if error.check() {
            Err(error)
        } else {
            Ok(profile)
        }
    }

    pub fn wait_for_frames(&self, timeout: u32) -> Result<Vec<Frame>, Error> {
        let mut error = Error::default();
        unsafe {
            let frames = rs2::rs2_pipeline_wait_for_frames(self.raw, timeout, error.inner());
            if error.check() {
                return Err(error);
            };
            let count = rs2::rs2_embedded_frames_count(frames, error.inner());
            if error.check() {
                return Err(error);
            };
            let mut res: Vec<Frame> = Vec::new();
            for i in 0..count {
                res.push(Frame {
                    raw: rs2::rs2_extract_frame(frames, i, error.inner()),
                });
                if error.check() {
                    return Err(error);
                };
            }
            rs2::rs2_release_frame(frames);
            Ok(res)
        }
    }
}

impl PipelineProfile {
    pub fn get_streams(&self) -> Result<Vec<StreamProfile>, Error> {
        let mut error = Error::default();
        unsafe {
            let stream_profiles = rs2::rs2_pipeline_profile_get_streams(self.raw, error.inner());
            if error.check() {
                return Err(error);
            };
            let stream_count = rs2::rs2_get_stream_profiles_count(stream_profiles, error.inner());
            if error.check() {
                return Err(error);
            };
            let mut streams: Vec<StreamProfile> = Vec::new();
            for i in 0..stream_count {
                streams.push(StreamProfile {
                    raw: rs2::rs2_get_stream_profile(stream_profiles, i, error.inner())
                        as *mut rs2::rs2_stream_profile,
                    clone: false,
                });
                if error.check() {
                    return Err(error);
                };
            }
            Ok(streams)
        }
    }

    pub fn get_stream(&self, stream_type: rs2::rs2_stream) -> Option<StreamProfile> {
        for stream in self.get_streams().unwrap() {
            if stream.get_data().unwrap().stream == stream_type {
                return Some(stream);
            }
        }
        None
    }

    pub fn get_device(&self) -> Result<Device, Error> {
        let mut error = Error::default();
        let device = Device {
            raw: unsafe { rs2::rs2_pipeline_profile_get_device(self.raw, error.inner()) },
        };
        if error.check() {
            Err(error)
        } else {
            Ok(device)
        }
    }
}
