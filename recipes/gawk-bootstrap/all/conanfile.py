import os
from conans import *


class GawkBootstrapConan(ConanFile):
    name = "gawk-bootstrap"
    description = "GNU version of awk"
    license = "GPL"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://ftp.gnu.org/pub/gnu/gawk/gawk-{self.version}.tar.gz")

    def build(self):
        args = [
            "--without-libsigsegv",
            f"--libexecdir={os.path.join(self.package_folder, 'lib')}",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(args=args, configure_dir=f"gawk-{self.version}")
        autotools.install()
