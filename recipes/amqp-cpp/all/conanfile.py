from conans import CMake, ConanFile, tools
import os


class AmqpCppConan(ConanFile):
    name = "amqp-cpp"
    settings = "os", "compiler", "build_type", "arch"
    license = "custom"
    description = "JPEG image codec with accelerated baseline compression and decompression"
    exports = "openssl.patch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/3.15.3@%s/stable" % self.user)

    def requirements(self):
        self.requires("openssl/1.1.1b@%s/stable" % self.user)

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
