use crate::error::Error;
use crate::pipeline::Pipeline;
use crate::pipeline_profile::PipelineProfile;
use rs2;

// Expose `rs2_format` and `rs2_stream` for external use.
pub use rs2::rs2_format;
pub use rs2::rs2_stream;

/// Struct representation of configuration `Config` that wraps around `rs2_config` handle. The
/// `Config` allows, in combination with `Pipeline`, to request filters for the streams and
/// `Device` selection and configuration.
pub struct Config {
    pub(crate) handle: *mut rs2::rs2_config,
}

/// Safe releasing of the `rs2_config` handle.
impl Drop for Config {
    fn drop(&mut self) {
        unsafe {
            rs2::rs2_delete_config(self.handle);
        }
    }
}

impl Config {
    /// Create a `Config` instance. The `Config` allows `Pipeline` users to request filters for the
    /// `Pipeline` `Stream`s and `Device` selection and configuration. This is an optional step in
    /// `Pipeline` creation, as the `Pipeline` resolves its streaming `Device` internally. `Config`
    /// provides its users a way to set the filters and test if there is no conflict with the
    /// pipeline requirements from the `Device`. It also allows the user to find a matching
    /// `Device` for the config filters and the `Pipeline`, in order to select a `Device`
    /// explicitly, and modify its controls before streaming starts.
    ///
    /// **Return value:**
    /// * **Ok(Config)** on success.
    /// * **Err(Error)** on failure.
    pub fn new() -> Result<Config, Error> {
        let mut error = Error::default();
        let config = Config {
            handle: unsafe { rs2::rs2_create_config(error.inner()) },
        };
        if error.check() {
            Err(error)
        } else {
            Ok(config)
        }
    }

    /// Enable a `Device` `Stream` explicitly, with selected parameters. The method allows the
    /// application to request a `Stream` with specific configuration. If no `Stream` is explicitly
    /// enabled, the `Pipeline` configures the `Device` and its `Stream`s according to the
    /// attached computer vision modules and processing blocks requirements, or default
    /// configuration for the first available `Device`. The application can configure any of the
    /// input `Stream` parameters according to its requirement, or set to 0 for don't care value.
    /// The `Config` accumulates the application calls for enable configuration methods, until the
    /// configuration is applied. Multiple enable `Stream` calls for the same `Stream` with
    /// conflicting parameters override each other, and the last call is maintained. Upon calling
    /// `resolve()`, the `Config` checks for conflicts between the application configuration
    /// requests and the attached computer vision modules and processing blocks requirements, and
    /// fails if conflicts are found. Before `resolve()` is called, no conflict check is done.
    ///    
    /// **Parameters:**
    /// * **stream** - Stream type to be enabled.
    /// * **index** - Stream index, used for multiple streams of the same type. -1 indicates any.
    /// * **width** - Stream image width - for images streams. 0 indicates any.
    /// * **height** - Stream image height - for images streams. 0 indicates any.
    /// * **format** - Stream data format - pixel format for images streams, of data type for other
    /// streams. `RS2_FORMAT_ANY` indicates any.
    /// * **framerate** - Stream frames per second. 0 indicates any.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(Error)** on failure.
    pub fn enable_stream(
        &self,
        stream: rs2_stream,
        index: i32,
        width: i32,
        height: i32,
        format: rs2_format,
        framerate: i32,
    ) -> Result<(), Error> {
        let mut error = Error::default();
        unsafe {
            rs2::rs2_config_enable_stream(
                self.handle,
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

    /// Enable all `Device` `Stream`s explicitly. The conditions and behavior of this method are
    /// similar to those of `enable_stream()`. This filter enables all raw `Streams` of the
    /// selected `Device`. The `Device` is either selected explicitly by the application, or by the
    /// `Pipeline` requirements or default. The list of `Stream`s is `Device` dependent.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(Error)** on failure.
    pub fn enable_all_streams(&self) -> Result<(), Error> {
        let mut error = Error::default();
        unsafe {
            rs2::rs2_config_enable_all_stream(self.handle, error.inner());
        }
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    /// Select a specific `Device` explicitly by its `serial` number, to be used by the `Pipeline`.
    /// The conditions and behavior of this method are similar to those of `enable_stream()`. This
    /// method is required if the application needs to set `Device` or `Sensor` settings prior to
    /// `Pipeline` streaming, to enforce the `Pipeline` to use the configured `Device`.
    ///    
    /// **Parameters:**
    /// * **serial** - `Device` serial number, as returned by `RS2_CAMERA_INFO_SERIAL_NUMBER`.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(Error)** on failure.
    pub fn enable_device(&self, serial: &str) -> Result<(), Error> {
        let mut error = Error::default();
        let s = std::ffi::CString::new(serial).expect("Failed to create CString");
        unsafe {
            rs2::rs2_config_enable_device(self.handle, s.as_ptr(), error.inner());
        }
        std::mem::forget(s);
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    /// Select a recorded `Device` from a `file`, to be used by the `Pipeline` through playback.
    /// The `Device` available `Stream`s are as recorded to the `file`, and `resolve()` considers
    /// only this `Device` and configuration as available. This request cannot be used if
    /// `enable_record_to_file()` is called for the current `Config`, and vise versa. By default,
    /// playback is repeated once the file ends. To control this, see
    /// 'enable_device_from_file_repeat_option()'.
    ///    
    /// **Parameters:**
    /// * **file** - The playback file of the `Device`.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(Error)** on failure.
    pub fn enable_device_from_file(&self, file: &str) -> Result<(), Error> {
        let mut error = Error::default();
        let s = std::ffi::CString::new(file).expect("Failed to create CString");
        unsafe {
            rs2::rs2_config_enable_device_from_file(self.handle, s.as_ptr(), error.inner());
        }
        std::mem::forget(s);
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    /// Select a recorded `Device` from a `file`, to be used by the `Pipeline` through playback.
    /// The `Device` available `Stream`s are as recorded to the `file`, and `resolve()` considers
    /// only this `Device` and configuration as available. This request cannot be used if
    /// `enable_record_to_file()` is called for the current `Config`, and vise versa.
    ///    
    /// **Parameters:**
    /// * **file** - The playback file of the `Device`.
    /// * **repeat** - If true, when file ends the playback starts again, in an infinite loop. If
    /// false, when `file` ends playback does not start again, and should by stopped manually by
    /// the user.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(Error)** on failure.
    pub fn enable_device_from_file_repeat_option(
        &self,
        file: &str,
        repeat: bool,
    ) -> Result<(), Error> {
        let mut error = Error::default();
        let s = std::ffi::CString::new(file).expect("Failed to create CString");
        unsafe {
            rs2::rs2_config_enable_device_from_file_repeat_option(
                self.handle,
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

    /// Requires that the resolved `Device` would be recorded to file. This request cannot be used
    /// if `enable_device_from_file()` is called for the current `Config`, and vise versa.
    ///    
    /// **Parameters:**
    /// * **file** - The desired file for the output record.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(Error)** on failure.
    pub fn enable_record_to_file(&self, file: &str) -> Result<(), Error> {
        let mut error = Error::default();
        let s = std::ffi::CString::new(file).expect("Failed to create CString");
        unsafe {
            rs2::rs2_config_enable_record_to_file(self.handle, s.as_ptr(), error.inner());
        }
        std::mem::forget(s);
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    /// Disable a `Device` `Stream` explicitly, to remove any requests on this `Stream` `type`. The
    /// stream can still be enabled due to `Pipeline` computer vision module request. This call
    /// removes any filter on the `Stream` configuration.
    ///    
    /// **Parameters:**
    ///	* **stream** - `Stream` type, for which the filters are cleared.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(Error)** on failure.
    pub fn disable_stream(&self, stream: rs2_stream) -> Result<(), Error> {
        let mut error = Error::default();
        unsafe {
            rs2::rs2_config_disable_stream(self.handle, stream, error.inner());
        }
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    /// Disable a `Device` indexed `Stream` explicitly, to remove any requests on this
    /// `StreamProfile`. The `Stream` can still be enabled due to `Pipeline` computer vision module
    /// request. This call removes any filter on the `Stream` configuration.
    ///    
    /// **Parameters:**
    ///	* **stream** - `Stream type`, for which the filters are cleared.
    ///	* **index** - `Stream index`, for which the filters are cleared.
    ///
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(Error)** on failure.
    pub fn disable_indexed_stream(&self, stream: rs2_stream, index: i32) -> Result<(), Error> {
        let mut error = Error::default();
        unsafe {
            rs2::rs2_config_disable_indexed_stream(self.handle, stream, index, error.inner());
        }
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    /// Disable all `Device` `Stream`s explicitly, to remove any requests on the `StreamsProfile`s.
    /// The `Stream`s can still be enabled due to `Pipeline` computer vision module request. This
    /// call removes any filter on the `Stream` configuration.
    ///    
    /// **Return value:**
    /// * **Ok()** on success.
    /// * **Err(Error)** on failure.
    pub fn disable_all_streams(&self) -> Result<(), Error> {
        let mut error = Error::default();
        unsafe {
            rs2::rs2_config_disable_all_streams(self.handle, error.inner());
        }
        if error.check() {
            Err(error)
        } else {
            Ok(())
        }
    }

    /// Resolve the configuration filters, to find a matching `Device` and `StreamsProfile`s. The
    /// method resolves the user configuration filters for the `Device` and `Stream`s, and combines
    /// them with the requirements of the computer vision modules and processing blocks attached to
    /// the pipeline. If there are no conflicts of requests, it looks for an available `Device`,
    /// which can satisfy all requests, and selects the first matching `StreamConfiguration`. In
    /// the absence of any request, the `rs2::config` selects the first available `Device` and the
    /// first color and `depth` `StreamConfiguration`s. The `PipelineProfile` selection during
    /// `start()` follows the same method. Thus, the selected profile is the same, if no change
    /// occurs to the available `Device`s occurs. Resolving the `Pipeline` configuration provides
    /// the application access to the pipeline selected `Device` for advanced control. The returned
    /// configuration is not applied to the `Device`, so the application doesn't own the `Device`
    /// `Sensor`s. However, the application can call `enable_device()`, to enforce the `Device`
    /// returned by this method is selected by `Pipeline` `start()`, and configure the `Device` and
    /// `Sensor`s options or extensions before streaming starts.
    ///    
    /// **Parameters:**
    ///	* **pipe** - The `Pipeline` for which the selected filters are applied.
    ///
    /// **Return value:**
    /// * **Ok(PipelineProfile)** on success.
    /// * **Err(Error)** on failure.
    pub fn resolve(&self, pipe: &Pipeline) -> Result<PipelineProfile, Error> {
        let mut error = Error::default();
        let pipe_profile = PipelineProfile {
            handle: unsafe { rs2::rs2_config_resolve(self.handle, pipe.handle, error.inner()) },
        };

        if error.check() {
            Err(error)
        } else {
            Ok(pipe_profile)
        }
    }

    /// Check if the `Config` can resolve the configuration filters, to find a matching `Device`
    /// and `StreamProfile`s. The resolution conditions are as described in `resolve()`.
    ///    
    /// **Parameters:**
    ///	* **pipe** - The pipeline for which the selected filters are applied.
    ///
    /// **Return value:**
    /// * **Ok(bool)** on success, determining whether the `Config` is valid.
    /// * **Err(Error)** on failure.
    pub fn can_resolve(&self, pipe: &Pipeline) -> Result<bool, Error> {
        let mut error = Error::default();
        let ret = unsafe { rs2::rs2_config_can_resolve(self.handle, pipe.handle, error.inner()) };
        if error.check() {
            Err(error)
        } else {
            if ret == 0 {
                Ok(false)
            } else {
                Ok(true)
            }
        }
    }
}
