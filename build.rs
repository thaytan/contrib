extern crate capnpc;

fn main() {
    ::capnpc::CompilerCommand::new()
        .file("src/rs_meta.capnp")
        .run()
        .expect("compiling schema");
}
