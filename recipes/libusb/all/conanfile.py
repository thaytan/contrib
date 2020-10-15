from conans import *


class LibUSBConan(ConanFile):
    description = "A cross-platform library to access USB devices"
    license = "LGPL-2.1"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "clang/[^10.0.1]",
        "autotools/[^1.0.0]",
    )
    requires = ("eudev/[^3.2.9]",)

    def source(self):
        tools.get(f"https://github.com/libusb/libusb/releases/download/v{self.version}/libusb-{self.version}.tar.bz2")

    def build(self):
        args = [
            "--disable-shared",
            "--enable-udev",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"libusb-{self.version}", args)
        autotools.install()
