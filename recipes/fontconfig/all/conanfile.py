import os
from glob import glob

from conans import *


class FontconfigConan(ConanFile):
    description = "A library for configuring and customizing font access"
    license = "Old MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/[^1.0.0]",
        "gperf/[^3.1]",
    )
    requires = (
        "base/[^1.0.0]",
        "freetype/[^2.10.1]",
        "libuuid/[^1.0.3]",
        "expat/[^2.2.7]",
    )

    def source(self):
        tools.get(f"https://gitlab.freedesktop.org/fontconfig/fontconfig/-/archive/{self.version}/fontconfig-{self.version}.tar.gz")

    def build(self):
        args = ["--disable-static"]
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()

    def package(self):
        with tools.chdir(self.package_folder + "/etc/fonts/conf.d"):
            for root, dirs, files in os.walk("."):
                for filename in files:
                    os.remove(filename)

        with tools.chdir(self.package_folder + "/etc/fonts/conf.d"):
            for root, dirs, files in os.walk(self.package_folder + "/share/fontconfig/conf.avail"):
                for filename in files:
                    os.symlink("../../../share/fontconfig/conf.avail/" + filename, filename)

    def package_info(self):
        self.env_info.FONTCONFIG_PATH.append(os.path.join(self.package_folder, "etc", "fonts"))
