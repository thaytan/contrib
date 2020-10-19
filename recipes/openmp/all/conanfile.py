from conans import *


class OpenmpConan(ConanFile):
    description = "LLVM OpenMP Runtime Library"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "cmake/[^3.18.4]",
        "libffi/[^3.3]",
        "elfutils/[^0.179]",
        "perl/[^5.30.0]",
    )

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/openmp-{self.version}.src.tar.xz")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["LIBOMP_ENABLE_SHARED"] = False
        cmake.definitions["OPENMP_ENABLE_LIBOMPTARGET"] = False
        cmake.definitions["LIBOMP_OMPT_SUPPORT"] = False
        cmake.configure(source_folder=f"openmp-{self.version}.src")
        cmake.build()
        cmake.install()
