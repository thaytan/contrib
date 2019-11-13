extern crate bindgen;

use std::env;
use std::path::PathBuf;

fn main() {
    println!("cargo:rustc-link-lib=k4a");

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
        .generate()
        .expect("Unable to generate bindings for `k4a`");

    let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    bindings
        .write_to_file(out_path.join("libk4a_bindings.rs"))
        .expect("Couldn't write bindings for `k4a`");
}
