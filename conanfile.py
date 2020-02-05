from conans import CMake, ConanFile, tools


class AmqpCppConan(ConanFile):
    name = "amqp-cpp"
    version = tools.get_env("GIT_TAG", "4.1.5")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    description = "JPEG image codec with accelerated baseline compression and decompression"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/3.15.3@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/CopernicaMarketingSoftware/AMQP-CPP/archive/v%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder="AMQP-CPP-%s" % self.version)
        cmake.build()
        cmake.install()
