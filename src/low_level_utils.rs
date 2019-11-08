/// Converts a `CString` to a Rust `String`.
///
/// **Parameters:**
/// * **ptr** - Pointer to the `CString`.
///
/// **Return value:**
/// * **String**
pub(crate) fn cstring_to_string(ptr: *const ::std::os::raw::c_char) -> String {
    unsafe {
        let bytes = std::ffi::CStr::from_ptr(ptr).to_bytes();
        std::str::from_utf8(bytes)
            .ok()
            .expect("Invalid UTF8 string")
            .to_string()
    }
}
