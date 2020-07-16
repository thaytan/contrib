from conans import *


class LlvmConan(ConanFile):
    name = "llvm"
    description = "Collection of modular and reusable compiler and toolchain technologies"
    license = "Apache"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"], "libc_build": ["system"]}
    build_requires = (
        "llvm-bootstrap/[^10.0.0]",
        "cmake-bootstrap/[^3.17.3]",
    )
    requires = (
        ("generators/[^1.0.0]", "private"),
        "libcxx/[^10.0.0]",
        "zlib/[^1.2.11]",
        "ncurses/[^6.2]",
        "libffi/[^3.3]",
    )

    def source(self):
        tools.get(f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/llvm-{self.version}.src.tar.xz")

    def build(self):
        cmake = CMake(self)

        # LLVM build options
        cmake.definitions["BUILD_SHARED_LIBS"] = True
        cmake.definitions["LLVM_BUILD_RUNTIME"] = True
        cmake.definitions["LLVM_INSTALL_UTILS"] = True
        cmake.definitions["LLVM_BUILD_DOCS"] = False
        cmake.definitions["LLVM_BUILD_EXAMPLES"] = False
        cmake.definitions["LLVM_BUILD_TESTS"] = False

        # LLVM enable options
        cmake.definitions["LLVM_ENABLE_ASSERTIONS"] = False
        cmake.definitions["LLVM_ENABLE_Z3_SOLVER"] = False
        cmake.definitions["LLVM_ENABLE_SPHINX"] = False
        cmake.definitions["LLVM_ENABLE_LIBXML2"] = False
        cmake.definitions["LLVM_ENABLE_FFI"] = True
        cmake.definitions["LLVM_ENABLE_LIBCXX"] = True
        cmake.definitions["LLVM_ENABLE_PIC"] = True
        cmake.definitions["LLVM_ENABLE_RTTI"] = True
        cmake.definitions["LLVM_ENABLE_TERMINFO"] = True
        cmake.definitions["LLVM_ENABLE_ZLIB"] = True

        env = {
            "CPLUS_INCLUDE_PATH": "",  # Use only llvm-bootstrap header files to avoid header conflicts with libcxx
        }
        with tools.environment_append(env):
            cmake.configure(source_folder=f"{self.name}-{self.version}.src")
            cmake.build()
            cmake.install()
