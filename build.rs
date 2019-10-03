extern crate capnpc;

fn main() {
    ::capnpc::CompilerCommand::new()
        .src_prefix("schema")
        .file("schema/rs_meta.capnp")
        .run()
        .expect("compiling schema");
}
