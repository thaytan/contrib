from conans import *
import os


class LibeventConan(ConanFile):
    description = "Event notification library https://libevent.org"
    license = "BSD-3-Clause"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    exports = "uninstall.patch"
    build_requires = (
        "env-generator/1.0.0",
        "cmake/3.15.3",
    )
    requires = (
        "openssl/1.1.1b",
        "zlib/[^1.2.11]",
    )

    def source(self):
        tools.get("https://github.com/libevent/libevent/releases/download/release-%s-stable/libevent-%s-stable.tar.gz" % (self.version, self.version))
        tools.patch(patch_file="uninstall.patch", base_path=os.path.join(self.source_folder, "libevent-%s-stable" % self.version))

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder="libevent-%s-stable" % self.version)
        cmake.build()
        cmake.install()
