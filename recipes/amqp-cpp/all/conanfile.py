from conans import *
import os


class AmqpCppConan(ConanFile):
    description = "JPEG image codec with accelerated baseline compression and decompression"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    exports = "openssl.patch"
    build_requires = ("cmake/3.15.3",)
    requires = (
        "base/[^1.0.0]",
        "openssl/1.1.1b",
    )

    def source(self):
        tools.get(f"https://github.com/CopernicaMarketingSoftware/AMQP-CPP/archive/v{self.version}.tar.gz")
        tools.patch(patch_file="openssl.patch", base_path=os.path.join(self.source_folder, f"AMQP-CPP-{self.version}"))

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["AMQP-CPP_BUILD_SHARED"] = "ON"
        cmake.definitions["AMQP-CPP_LINUX_TCP"] = "ON"
        cmake.configure(source_folder=f"AMQP-CPP-{self.version}")
        cmake.build()
        cmake.install()
