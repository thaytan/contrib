extern crate bindgen;
extern crate pkg_config;

use std::env;
use std::path::PathBuf;

fn main() {
    let libk4a = pkg_config::Config::new()
        .atleast_version("1.3.0")
        .probe("k4a");

    // Determine include paths for `libk4a` if found with pkgconfig
    // Otherwise use local installation
    let mut libk4a_include_dirs: Vec<String> = Vec::new();
    if let Ok(libk4a) = libk4a {
        libk4a_include_dirs = libk4a
            .include_paths
            .iter()
            .map(|x| ["-I", x.to_str().unwrap()].concat())
            .collect();
    } else {
        println!("cargo:rustc-link-lib=k4a");
        println!("cargo:rustc-link-lib=k4arecord");
    }

    let bindings = bindgen::Builder::default()
        .header("wrapper.h")
        .rustified_enum("k4a_result_t")
        .rustified_enum("k4a_buffer_result_t")
        .rustified_enum("k4a_wait_result_t")
        .rustified_enum("k4a_log_level_t")
        .rustified_enum("k4a_depth_mode_t")
        .rustified_enum("k4a_color_resolution_t")
        .rustified_enum("k4a_image_format_t")
        .rustified_enum("k4a_transformation_interpolation_type_t")
        .rustified_enum("k4a_fps_t")
        .rustified_enum("k4a_color_control_command_t")
        .rustified_enum("k4a_color_control_mode_t")
        .rustified_enum("k4a_wired_sync_mode_t")
        .rustified_enum("k4a_calibration_type_t")
        .rustified_enum("k4a_calibration_model_type_t")
        .rustified_enum("k4a_firmware_build_t")
        .rustified_enum("k4a_firmware_signature_t")
        .rustified_enum("k4a_stream_result_t")
        .rustified_enum("k4a_playback_seek_origin_t")
        .clang_args(libk4a_include_dirs)
        .generate()
        .expect("Unable to generate bindings for `k4a`");

    let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    bindings
        .write_to_file(out_path.join("libk4a_bindings.rs"))
        .expect("Couldn't write bindings for `k4a`");
}
