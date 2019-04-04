fn main() {
    pkg_config::Config::new().atleast_version("0.1").probe("depth-meta").unwrap();
}
