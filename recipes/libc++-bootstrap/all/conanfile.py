import os
from conans import *
import shutil


class LibcppBootstrapConan(ConanFile):
    description = "LLVM C++ Standard Library"
    license = "custom"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = (
        "clang-bootstrap/[^10.0.0]",
        "cmake-bootstrap/[^3.17.3]",
        "libunwind-bootstrap/[^1.3.1]",
        "linux-headers/[^5.4.50]",
    )
    requires = (
        "musl/[^1.2.0]",
        "libcxxrt/[^4.0.10]",
    )

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/llvm-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libcxx-{self.version}.src.tar.xz")
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/libcxxabi-{self.version}.src.tar.xz")
        shutil.move(f"llvm-{self.version}.src", f"llvm-{self.version}")
        shutil.move(f"libcxx-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "libcxx"))
        shutil.move(f"libcxxabi-{self.version}.src", os.path.join(f"llvm-{self.version}", "projects", "libcxxabi"))
        # shutil.move(f"libcxx-{self.version}.src", f"libcxx-{self.version}")

        # shutil.move(f"libcxx-{self.version}.src", "libcxx")
        # shutil.move(f"libcxxabi-{self.version}.src", "libcxxabi")

    def build(self):
        # libcxx_include = os.path.join(self.build_folder, f"llvm-{self.version}", "projects", "libcxx", "include")
        libcxx_include = os.path.join(self.build_folder, f"llvm-{self.version}", "projects", "libcxx", "include")
        libcxxabi_include = os.path.join(self.build_folder, f"llvm-{self.version}", "projects", "libcxxabi", "include")
        libunwind_include = os.path.join(self.deps_cpp_info["libunwind-bootstrap"].rootpath, "include")
        clang_include = os.path.join(self.deps_cpp_info["clang-bootstrap"].rootpath, "lib", "clang", self.version, "include")
        # musl_include = os.environ["MUSL_INCLUDE_PATH"]
        env = {
            "CC": "musl-clang",
            "CXX": "musl-clang++",
            # "CFLAGS": f"-isystem {musl_include}",
            "CXXFLAGS": f"-stdlib=libc++ -isystem {libcxx_include} -isystem {libcxxabi_include} -isystem {libunwind_include} -isystem {clang_include}",
            # "CXXFLAGS": f"-stdlib=libc++ -isystem {libcxx_include} -isystem {libcxxabi_include} -isystem {libunwind_include} -isystem {musl_include} -isystem {clang_include}",
            # "CXXFLAGS": f"-stdlib=libc++ -isystem {libunwind_include} -isystem {musl_include} -isystem {clang_include}",
        }
        # with tools.environment_append(env):
        #    cmake = CMake(self, generator="Ninja")
        #    cmake.definitions["LIBCXX_HAS_MUSL_LIBC"] = True
        #    # cmake.definitions["CMAKE_CC_COMPILER"] = "musl-clang"
        #    # cmake.definitions["CMAKE_CXX_COMPILER"] = "musl-clang++"
        #    cmake.definitions["LIBCXX_CXX_ABI"] = "libcxxrt"
        #    # cmake.definitions["CMAKE_C_COMPILER_FORCE"] = True
        #    # cmake.definitions["CMAKE_CXX_COMPILER_FORCE"] = True

        #    # cmake.definitions["LLVM_ENABLE_PROJECTS"] = "libcxx;libcxxabi"
        #    cmake.configure(source_folder=f"libcxx-{self.version}")
        #    cmake.build()
        #    cmake.install()
        #    # cmake.install(target="install-cxx")
        #    # cmake.install(target="install-cxxabi")
        with tools.environment_append(env):
            cmake = CMake(self, generator="Ninja")
            cmake.definitions["LIBCXX_HAS_MUSL_LIBC"] = True
            # cmake.definitions["CMAKE_CC_COMPILER"] = "musl-clang"
            # cmake.definitions["CMAKE_CXX_COMPILER"] = "musl-clang++"
            cmake.definitions["LIBCXX_CXX_ABI"] = "libcxxabi"
            # cmake.definitions["LIBCXXABI_LIBCXX_INCLUDES"] = libcxx_include
            cmake.definitions["LIBCXX_INSTALL_EXPERIMENTAL_LIBRARY"] = False
            cmake.definitions["HAVE_CXX_ATOMICS_WITHOUT_LIB"] = True
            cmake.definitions["HAVE_CXX_ATOMICS64_WITHOUT_LIB"] = True
            # cmake.definitions["CMAKE_C_COMPILER_FORCE"] = True
            # cmake.definitions["CMAKE_CXX_COMPILER_FORCE"] = True

            # cmake.definitions["LLVM_ENABLE_PROJECTS"] = "libcxx;libcxxabi"
            cmake.configure(source_folder=f"llvm-{self.version}")
            cmake.build(target="cxx")
            cmake.build(target="cxx_experimental")
            cmake.install(target="install-libcxx")
            cmake.install(target="install-libcxxabi")

