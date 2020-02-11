from conans import CMake, ConanFile, tools


class LibeventConan(ConanFile):
    name = "libevent"
    version = tools.get_env("GIT_TAG", "2.1.11")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "BSD-3"
    description = "C++ library for asynchronous non-blocking communication with RabbitMQ"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/3.15.3@%s/stable" % self.user)

    def requirements(self):
        self.requires("openssl/1.1.1b@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/libevent/libevent/releases/download/release-%s-stable/libevent-%s-stable.tar.gz" % (self.version, self.version))

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder="libevent-%s-stable" % self.version)
        cmake.build()
        cmake.install()
