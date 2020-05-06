from conans import AutoToolsBuildEnvironment, ConanFile, tools, CMake

class ConanWebP(ConanFile):
    name = "webp"
    version = tools.get_env("GIT_TAG", "1.1.0")
    license = "BSD"
    description = "library to encode and decode images in WebP format"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/webmproject/libwebp/archive/v%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder="libwebp-%s" % (self.version))
        cmake.build()
        cmake.install()
