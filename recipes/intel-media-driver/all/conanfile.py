from conans import *


class IntelMediaDriverConan(ConanFile):
    description = "Intel Media Driver for VAAPI — Broadwell+ iGPUs"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "cmake/[^3.18.4]",
    )
    requires = (
        "intel-gmmlib/[^20.3.2]",
        "libva/[^2.9.0]",
        "libpciaccess/[^0.16]",
    )

    def source(self):
        tools.get(f"https://github.com/intel/media-driver/archive/intel-media-{self.version}.tar.gz")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=f"intel-media-driver-{self.version}")
        cmake.build()
        cmake.install()
