from conans import CMake, ConanFile, tools


class MinuzConan(ConanFile):
    name = "miniz"
    description = "Single C source file zlib-replacement library"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/richgel999/miniz/archive/%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_dir="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()
