extern crate capnpc;

fn main() {
    gst_plugin_version_helper::get_info();
    ::capnpc::CompilerCommand::new()
        .src_prefix("schema")
        .file("schema/rs_meta.capnp")
        .run()
        .expect("compiling schema");
}
