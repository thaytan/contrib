import os

from conans import CMake, ConanFile, tools


class LibjpegTurboConan(ConanFile):
    name = "libjpeg-turbo"
    version = tools.get_env("GIT_TAG", "2.0.4")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    description = "JPEG image codec with accelerated baseline compression and decompression"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("yasm/1.3.0@%s/stable" % self.user)
        self.build_requires("cmake/3.15.3@%s/stable" % self.user)

    def requirements(self):
        self.requires("zlib/[>=1.2.11]@%s/stable" % self.user)

    def source(self):
        tools.get("https://downloads.sourceforge.net/project/libjpeg-turbo/{0}/libjpeg-turbo-{0}.tar.gz".format(self.version))

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["WITH_JPEG8"] = True
        cmake.definitions["CMAKE_INSTALL_LIBDIR"] = os.path.join(self.package_folder, "lib")
        cmake.definitions["CMAKE_INSTALL_INCLUDEDIR"] = os.path.join(self.package_folder, "include")
        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()
