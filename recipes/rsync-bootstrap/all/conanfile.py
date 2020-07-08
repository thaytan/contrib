from conans import *


class RsyncBootstrapConan(ConanFile):
    name = "rsync-bootstrap"
    description = "A fast and versatile file copying tool for remote and local files"
    license = "GPL3"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    requires = ("openssl-bootstrap/[^3.0.0-alpha4]",)

    def source(self):
        tools.get(f"https://download.samba.org/pub/rsync/src/rsync-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-static",
            "--disable-xxhash",
            "--disable-zstd",
            "--disable-lz4",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(args=args, configure_dir=f"rsync-{self.version}")
        autotools.make()
        autotools.install()
