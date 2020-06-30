from conans import *
import os


class AmqpCppConan(ConanFile):
    description = "JPEG image codec with accelerated baseline compression and decompression"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    exports = "openssl.patch"
    build_requires = (
        "generators/1.0.0",
        "cmake/3.15.3",
    )
    requires = (
        "openssl/1.1.1b",
    )

    def source(self):
        tools.get("https://github.com/CopernicaMarketingSoftware/AMQP-CPP/archive/v%s.tar.gz" % self.version)
        tools.patch(patch_file="openssl.patch", base_path=os.path.join(self.source_folder, "AMQP-CPP-%s" % self.version))

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["AMQP-CPP_BUILD_SHARED"] = "ON"
        cmake.definitions["AMQP-CPP_LINUX_TCP"] = "ON"
        cmake.configure(source_folder="AMQP-CPP-%s" % self.version)
        cmake.build()
        cmake.install()
