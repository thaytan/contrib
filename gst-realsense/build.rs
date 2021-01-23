extern crate capnpc;

fn main() {
    gst_plugin_version_helper::get_info();
    ::capnpc::CompilerCommand::new()
        .src_prefix("src/schema")
        .file("src/schema/rs_meta.capnp")
        .run()
        .expect("compiling schema");
}
