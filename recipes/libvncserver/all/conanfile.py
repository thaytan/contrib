from conans import *


class LibvncserverConan(ConanFile):
    description = "Cross-platform C libraries that allow you to easily implement VNC server or client functionality"
    license = "Apache"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("cmake/[^3.15.3]",)
    requires = (
        "base/[^1.0.0]",
        "libpng/[^1.6.37]",
        "openssl/[^1.1.1b]",
    )

    def source(self):
        tools.get(f"https://github.com/LibVNC/libvncserver/archive/LibVNCServer-{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder=f"libvncserver-LibVNCServer-{self.version}")
        cmake.build()
        cmake.install()
