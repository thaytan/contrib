extern crate capnpc;

fn main() {
    pkg_config::Config::new().probe("depth-meta").unwrap();

    ::capnpc::CompilerCommand::new()
        .src_prefix("src/schema")
        .file("src/schema/camera_meta.capnp")
        .run()
        .expect("compiling schema");
}
