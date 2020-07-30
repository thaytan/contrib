import os
from conans import *


class LinuxHeadersBootstrapConan(ConanFile):
    name = "linux-headers-bootstrap"
    description = "Linux system headers"
    license = "GPL-2.0-only"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}

    def source(self):
        tools.get(f"https://cdn.kernel.org/pub/linux/kernel/v{self.version.split('.')[0]}.x/linux-{self.version}.tar.xz")

    def build(self):
        arch = {"x86_64": "x86_64", "armv8": "arm64"}[str(self.settings.arch_build)]
        with tools.chdir(f"linux-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make(target="headers_install", args=[f"ARCH={arch}", f'INSTALL_HDR_PATH="{self.package_folder}"'])

    def package_info(self):
        self.env_info.CPATH.append(os.path.join(self.package_folder, "include"))
