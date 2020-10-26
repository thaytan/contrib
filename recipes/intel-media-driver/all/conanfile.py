import os
from conans import *


class IntelMediaDriverConan(ConanFile):
    description = "Intel Media Driver for VAAPI Broadwell iGPUs"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("cmake/[^3.18.4]",)
    requires = (
        "intel-gmmlib/[^20.3.2]",
        "libva/[^2.9.0]",
        "libpciaccess/[^0.16]",
    )

    def source(self):
        tools.get(f"https://github.com/intel/media-driver/archive/intel-media-{self.version}.tar.gz")

    def build(self):
        os.environ["CPATH"] += ":" + ":".join(self.deps_cpp_info["libx11"].include_paths + self.deps_cpp_info["xorgproto"].include_paths)
        cmake = CMake(self)

        # (Maybe) needed to pass tests with clang
        # cmake.definitions["BYPASS_MEDIA_ULT"] = True
        # os.environ["CXXFLAGS"] += " -fno-semantic-interposition"

        cmake.configure(source_folder=f"media-driver-intel-media-{self.version}")
        cmake.build()
        cmake.install()
