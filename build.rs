extern crate capnpc;

fn main() {
    pkg_config::Config::new()
        .atleast_version("0.2.0")
        .probe("depth-meta")
        .unwrap();

    ::capnpc::CompilerCommand::new()
        .src_prefix("schema")
        .file("schema/camera_meta.capnp")
        .run()
        .expect("compiling schema");
}
