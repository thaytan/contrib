extern crate bindgen;

use std::env;
use std::path::PathBuf;

fn main() {
    //pkg_config::Config::new().atleast_version("1.15.1").probe("gstreamer-video-1.0").unwrap();

    //let pkgs = ["gstreamer-1.0", "gstreamer-video-1.0"];
    //let mut all_path_args: Vec<String> = [].to_vec();

    //for pkg in pkgs.iter() {
    //    let mut config = pkg_config::Config::new();
    //    config.atleast_version("1.15.1");
    //    let mut path_args : Vec<String> = match config.probe(pkg) {
    //        Ok(library) => library.include_paths.iter().map(|x| ["-I", x.to_str().unwrap()].concat()).collect(),
    //        Err(err) => std::panic!(err)
    //    };
    //    all_path_args.append(&mut path_args);
    //}


    //let bindings = bindgen::Builder::default()
    //    .layout_tests(false)
    //    .generate_comments(false)
    //    .header("src/color-meta.h")
    //    .clang_args(all_path_args)
    //    .generate()
    //    .expect("Unable to generate bindings");

    //let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    //bindings
    //    .write_to_file(out_path.join("bindings.rs"))
    //    .expect("Couldn't write bindings!");
}
