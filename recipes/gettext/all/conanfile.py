import os
from conans import *


class GettextConan(ConanFile):
    description = "GNU internationalization library"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    license = "GPL"
    build_requires = (
        "clang/[^10.0.1]",
        "make/[^4.3]",
    )

    def source(self):
        tools.get(f"https://ftp.gnu.org/pub/gnu/gettext/gettext-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-shared"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"gettext-{self.version}", args)
        autotools.make()
        autotools.install()

    def package_info(self):
        self.env_info.gettext_datadir.append(os.path.join(self.package_folder, "share", "gettext"))
