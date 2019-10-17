from conans import CMake, ConanFile, tools


class CclsConan(ConanFile):
    name = "ccls"
    version = tools.get_env("GIT_TAG", "0.20190823.3")
    license = "Apache"
    description = "C/C++ language server supporting cross references, hierarchies, completion and semantic highlighting"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("clang/[>=9.0.0]@%s/stable" % self.user)
        self.requires("rapidjson/master@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/MaskRay/ccls/archive/%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.build()
        cmake.install()
