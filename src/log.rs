use crate::error;
use rs2;

pub use rs2::rs2_log_severity;

pub fn log_to_console(min_severity: rs2_log_severity) {
    let mut error = error::Error::default();
    unsafe {
        rs2::rs2_log_to_console(min_severity, error.inner());
    }
    error.check();
}
