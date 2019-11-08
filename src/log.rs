use crate::error::Error;
use rs2;

// Expose `rs2_log_severity` for external use.
pub use rs2::rs2_log_severity;

/// Determine the level of severity to be logged to console.
///
/// **Return value:**
/// * **Ok()** on success.
/// * **Err(Error)** on failure.
pub fn log_to_console(min_severity: rs2_log_severity) -> Result<(), Error> {
    let mut error = Error::default();
    unsafe {
        rs2::rs2_log_to_console(min_severity, error.inner());
    }
    if error.check() {
        Err(error)
    } else {
        Ok(())
    }
}
