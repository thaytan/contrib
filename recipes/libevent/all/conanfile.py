from conans import *
import os


class LibeventConan(ConanFile):
    description = "Event notification library https://libevent.org"
    license = "BSD-3-Clause"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    exports = "uninstall.patch"
    build_requires = (
        "env-generator/1.0.0",
        "cmake/3.15.3",
    )
    requires = (
        "base/[^1.0.0]",
        "openssl/1.1.1b",
        "zlib/[^1.2.11]",
    )

    def source(self):
        tools.get(f"https://github.com/libevent/libevent/releases/download/release-{self.version}-stable/libevent-{self.version}-stable.tar.gz")
        tools.patch(patch_file=f"uninstall.patch", base_path=os.path.join(self.source_folder, "libevent-{self.version}-stable"))

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder=f"libevent-{self.version}-stable")
        cmake.build()
        cmake.install()
