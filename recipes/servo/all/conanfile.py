import os
import shutil

from conans import *


class ServoConan(ConanFile):
    description = "The Servo Browser Engine"
    license = "MIT", "Apache"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "cmake/[^3.15.3]",
        "python/[^3.7.4]",
        "python-virtualenv/[^3.7.4]",
        "python-pillow/[^7.1.2]",
        "rustup/[^1.21.1]",
    )
    requires = (
        "base/[^1.0.0]",
        "openssl/[^1.1.1b]",
        "dbus/[^1.12.16]",
        "libx11/[^1.6.8]",
        "libunwind/[^1.3.1]",
        "gstreamer/[^1.16.2]",
        "gstreamer-plugins-base/[^1.16.2]",
        "gstreamer-plugins-bad/[^1.16.2]",
    )

    def source(self):
        tools.get(f"https://github.com/noverby/servo/archive/{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("echo $PATH")
            self.run("./mach build -r")
