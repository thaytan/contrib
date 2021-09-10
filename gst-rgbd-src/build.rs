extern crate capnpc;

fn main() {
    gst_plugin_version_helper::info();
    ::capnpc::CompilerCommand::new()
        .src_prefix("src/realsense/schema")
        .file("src/realsense/schema/rs_meta.capnp")
        .run()
        .expect("compiling schema");
}
