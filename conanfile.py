from conans import CMake, ConanFile, tools


class MinuzConan(ConanFile):
    name = "miniz"
    version = tools.get_env("GIT_TAG", "2.1.0")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Single C source file zlib-replacement library"
    license = "ZLIB"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "x11": [True, False],
    }
    default_options = ("x11=True", )
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/richgel999/miniz/archive/%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_dir="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()
