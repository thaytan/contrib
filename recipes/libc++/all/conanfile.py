import os
import shutil
from conans import *


class LibcppConan(ConanFile):
    name = "libc++"
    description = "LLVM C++ Standard Library"
    license = "custom"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "clang-bootstrap/[^10.0.0]",
        "cmake-bootstrap/[^3.17.3]",
        "libunwind-bootstrap/[^.0.0]",
        "linux-headers/[^5.4.50]",
    )
    requires = ("musl/[^1.2.0]",)

    def source(self):
        # tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/llvm-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libcxx-{self.version}.src.tar.xz")
        # tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libcxxabi-{self.version}.src.tar.xz")
        # shutil.move(f"llvm-{self.version}.src", f"llvm-{self.version}")
        # shutil.move(f"libcxx-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "libcxx"))
        shutil.move(f"libcxx-{self.version}.src", f"libcxx-{self.version}")
        # shutil.move(f"libcxxabi-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "libcxxabi"))

        # shutil.move(f"libcxx-{self.version}.src", "libcxx")
        # shutil.move(f"libcxxabi-{self.version}.src", "libcxxabi")

    def build(self):
        libcxx_include = os.path.join(self.build_folder, f"llvm-{self.version}", "projects", "libcxx", "include")
        libunwind_include = os.path.join(self.deps_cpp_info["libunwind-bootstrap"].rootpath, "include")
        env = {
            "CC": "musl-clang",
            "CXX": "musl-clang++",
            "CFLAGS": "-isystem " + os.environ["MUSL_INCLUDE_PATH"],
            "CXXFLAGS": f"-stdlib=libc++ -isystem {libcxx_include} -isystem {libunwind_include}",
        }
        with tools.environment_append(env):
            cmake = CMake(self, generator="Ninja")
            cmake.definitions["LIBCXX_HAS_MUSL_LIBC"] = True
            # cmake.definitions["CMAKE_CC_COMPILER"] = "musl-clang"
            # cmake.definitions["CMAKE_CXX_COMPILER"] = "musl-clang++"
            cmake.definitions["LIBCXX_CXX_ABI"] = "libcxxabi"
            # cmake.definitions["CMAKE_C_COMPILER_FORCE"] = True
            # cmake.definitions["CMAKE_CXX_COMPILER_FORCE"] = True

            # cmake.definitions["LLVM_ENABLE_PROJECTS"] = "libcxx;libcxxabi"
            cmake.configure(source_folder=f"libcxx-{self.version}")
            cmake.build()
            cmake.install()
            # cmake.install(target="install-cxx")
            # cmake.install(target="install-cxxabi")
        # with tools.environment_append(env):
        #    cmake = CMake(self, generator="Ninja")
        #    cmake.definitions["LIBCXX_HAS_MUSL_LIBC"] = True
        #    # cmake.definitions["CMAKE_CC_COMPILER"] = "musl-clang"
        #    # cmake.definitions["CMAKE_CXX_COMPILER"] = "musl-clang++"
        #    # cmake.definitions["LIBCXX_CXX_ABI"] = "libcxxabi"
        #    # cmake.definitions["LIBCXXABI_LIBCXX_INCLUDES"] = libcxx_include
        #    cmake.definitions["LIBCXX_INSTALL_EXPERIMENTAL_LIBRARY"] = False
        #    # cmake.definitions["CMAKE_C_COMPILER_FORCE"] = True
        #    # cmake.definitions["CMAKE_CXX_COMPILER_FORCE"] = True

        #    # cmake.definitions["LLVM_ENABLE_PROJECTS"] = "libcxx;libcxxabi"
        #    cmake.configure(source_folder=f"llvm-{self.version}")
        #    cmake.build(target="cxx")
        #    cmake.build(target="cxx_experimental")
        #    cmake.install(target="install-libcxx")
        #    cmake.install(target="install-libcxxabi")
