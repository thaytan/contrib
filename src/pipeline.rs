use crate::context::Context;
use crate::config::Config;
use crate::error::Error;
use crate::frame::Frame;
use crate::pipeline_profile::PipelineProfile;
use rs2;

/// Struct representation of `Pipeline` that wraps around `rs2_pipeline` handle. The `Pipeline`
/// simplifies the user interaction with the `Device` and computer vision processing modules. The
/// class abstracts the camera configuration and streaming, and the vision modules triggering and
/// threading. It lets the application focus on the computer vision output of the modules, or the
/// device output data. The `Pipeline` can manage computer vision modules, which are implemented as
/// a processing blocks. The `Pipeline` is the consumer of the processing block interface, while
/// the application consumes the computer vision interface.
pub struct Pipeline {
    pub(crate) handle: *mut rs2::rs2_pipeline,
}

/// Safe releasing of the `rs2_pipeline` handle.
impl Drop for Pipeline {
    fn drop(&mut self) {
        unsafe {
            rs2::rs2_delete_pipeline(self.handle);
        }
    }
}

unsafe impl Send for Pipeline {}
unsafe impl Sync for Pipeline {}

impl Pipeline {
    /// Create a new `Pipeline` instance.
    ///
    /// **Parameters:**
    /// * **ctx** - The `Context` for which to create a new `Pipeline`.
    ///
    /// **Return value:**
    /// * **Ok(Pipeline)** on success.
    /// * **Err(Error)** on failure.
    pub fn new(ctx: &Context) -> Result<Pipeline, Error> {
        let mut error = Error::default();
        let pipeline = Pipeline {
            handle: unsafe { rs2::rs2_create_pipeline(ctx.handle, error.inner()) },
        };
        if error.check() {
            Err(error)
        } else {
            Ok(pipeline)
        }
    }

    /// Start the `Pipeline` streaming with its default configuration. The pipeline streaming loop
    /// captures samples from the `Device`, and delivers them to the attached computer vision
    /// modules and processing blocks, according to each module requirements and threading model.
    /// During the loop execution, the application can access the camera streams by calling
    /// `wait_for_frames()` or `poll_for_frames()`. The streaming loop runs until the `Pipeline` is
    /// stopped. Starting the `Pipeline` is possible only when it is not started. If the `Pipeline`
    /// was started, an exception is raised.
    ///
    /// **Return value:**
    /// * **Ok(PipelineProfile)** on success.
    /// * **Err(Error)** on failure.
    pub fn start(&self) -> Result<PipelineProfile, Error> {
        let mut error = Error::default();
        let profile = PipelineProfile {
            handle: unsafe { rs2::rs2_pipeline_start(self.handle, error.inner()) },
        };
        if error.check() {
            Err(error)
        } else {
            Ok(profile)
        }
    }

    /// Start the `Pipeline` streaming according to the `Config`. The `Pipeline` streaming loop
    /// captures samples from the `Device`, and delivers them to the attached computer vision
    /// modules and processing blocks, according to each module requirements and threading model.
    /// During the loop execution, the application can access the camera streams by calling
    /// `wait_for_frames()` or `poll_for_frames()`. The streaming loop runs until the `Pipeline` is
    /// stopped. Starting the `Pipeline` is possible only when it is not started. If the `Pipeline`
    /// was started, an exception is raised. The `Pipeline` selects and activates the `Device` upon
    /// start, according to configuration or a default configuration. The `Pipeline` tries to
    /// activate the `Config::resolve()` result. If the application requests are conflicting with
    /// `Pipeline` computer vision modules or no matching `Device` is available on the platform,
    /// the method fails. Available configurations and `Device`s may change between config resolve()
    ///  call and `Pipeline` start, in case `Device`s are connected or disconnected, or another
    /// application acquires ownership of a device.
    ///
    /// **Parameters:**
    /// * **config** - A `Config` with requested filters on the `Pipeline` configuration.
    ///
    /// **Return value:**
    /// * **Ok(PipelineProfile)** on success.
    /// * **Err(Error)** on failure.
    pub fn start_with_config(
        &self,
        rs2_config: &Config,
    ) -> Result<PipelineProfile, Error> {
        let mut error = Error::default();
        let profile = PipelineProfile {
            handle: unsafe {
                rs2::rs2_pipeline_start_with_config(self.handle, rs2_config.handle, error.inner())
            },
        };
        if error.check() {
            Err(error)
        } else {
            Ok(profile)
        }
    }

    /// Stop the `Pipeline` streaming. The `Pipeline` stops delivering samples to the attached
    /// computer vision modules and processing blocks, stops the device streaming and releases the
    /// device resources used by the `Pipeline`. It is the application's responsibility to release
    /// any frame reference it owns. The method takes effect only after `start()` was called,
    /// otherwise an exception is raised.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(Error)** on failure.
    pub fn stop(&self) -> Result<(), Error> {
        let mut error = Error::default();
        unsafe {
            rs2::rs2_pipeline_stop(self.handle, error.inner());
        }
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    /// Wait until a new set of `Frame`s becomes available. The `Frame`s set includes
    /// time-synchronized `Frame`s of each enabled stream in the pipeline. In case of different
    /// frame rates of the streams, the `Frame`s set include a matching frame of the slow stream,
    /// which may have been included in previous `Frame`s set. The method blocks the calling thread,
    ///  and fetches the latest unread `Frame`s set. Device `Frame`s, which were produced while the
    /// function wasn't called, are dropped. To avoid frame drops, this method should be called as
    /// fast as the device frame rate. The application can maintain the `Frame`s handles to defer
    /// processing. However, if the application maintains too long history, the device may lack
    /// memory resources to produce new `Frame`s, and the following call to this method shall fail
    /// to retrieve new frames, until resources become available.
    ///
    /// **Parameters:**
    /// * **timeout** - Max time in milliseconds to wait until `Error` is returned.
    ///
    /// **Return value:**
    /// * **Ok(Vec<Frame>)** on success.
    /// * **Err(Error)** on failure.
    pub fn wait_for_frames(&self, timeout: u32) -> Result<Vec<Frame>, Error> {
        let mut error = Error::default();
        unsafe {
            let frames = rs2::rs2_pipeline_wait_for_frames(self.handle, timeout, error.inner());
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
                    handle: rs2::rs2_extract_frame(frames, i, error.inner()),
                });
                if error.check() {
                    return Err(error);
                };
            }
            rs2::rs2_release_frame(frames);
            Ok(res)
        }
    }

    /// Wait until a new set of `Frame`s becomes available. The `Frame`s set includes
    /// time-synchronized `Frame`s of each enabled stream in the pipeline. The method blocks the
    /// calling thread, and fetches the latest unread `Frame`s set. Device `Frame`s, which were
    /// produced while the function wasn't called, are dropped. To avoid `Frame` drops, this method
    /// should be called as fast as the device `Frame` rate. The application can maintain the
    /// `Frame`s handles to defer processing. However, if the application maintains too long
    /// history, the device may lack memory resources to produce new `Frame`s, and the following
    /// call to this method shall fail to retrieve new `Frame`s, until resources are retained.
    ///
    /// **Parameters:**
    /// * **timeout** - Max time in milliseconds to wait until `Error` is returned.
    ///
    /// **Return value:**
    /// * **Ok(Vec<Frame>)** on success.
    /// * **Err(Error)** on failure.
    pub fn try_wait_for_frames(&self, _timeout: u32) -> Result<Vec<Frame>, Error> {
        unimplemented!();
    }

    /// Check if a new set of `Frame`s is available and retrieve the latest undelivered set. The
    /// `Frame`s set includes time-synchronized `Frame`s of each enabled `Stream` in the
    /// `Pipeline`. The method returns without blocking the calling thread, with status of new
    /// `Frame`s available or not. If available, it fetches the latest `Frame`s set. Device
    /// `Frame`s, which were produced while the function wasn't called, are dropped. To avoid
    /// `Frame` drops, this method should be called as fast as the device `Frame` rate. The
    /// application can maintain the `Frame`s handles to defer processing. However, if the
    /// application maintains too long history, the device may lack memory resources to produce new
    /// `Frame`s, and the following calls to this method shall return no new `Frame`s, until
    /// resources become available.
    ///
    /// **Return value:**
    /// * **Ok(Vec<Frame>)** on success.
    /// * **Err(Error)** on failure.
    pub fn poll_for_frames(&self) -> Result<Vec<Frame>, Error> {
        unimplemented!();
    }

    /// Return the active `Device` and `Stream`s profiles, used by the `Pipeline` as
    /// `PipelineProfile`. The `Pipeline` streams profiles are selected during `start()`. The
    /// method returns a valid result only when the `Pipeline` is active - between calls to
    /// `start()` and `stop()`. After stop() is called, the `Pipeline` doesn't own the device, thus,
    ///  the `Pipeline` selected device may change in subsequent activations.
    ///
    /// **Parameters:**
    /// * **timeout** - Max time in milliseconds to wait until `Error` is returned.
    ///
    /// **Return value:**
    /// * **Ok(PipelineProfile)** on success.
    /// * **Err(Error)** on failure.
    pub fn get_active_profile(&self) -> Result<PipelineProfile, Error> {
        let mut error = Error::default();
        let profile = PipelineProfile {
            handle: unsafe { rs2::rs2_pipeline_get_active_profile(self.handle, error.inner()) },
        };
        if error.check() {
            Err(error)
        } else {
            Ok(profile)
        }
    }
}
