from conans import ConanFile, CMake, tools

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "4.3.1"
    except:
        return None

class LibzmqConan(ConanFile):
    name = "libzmq"
    version = get_version()
    description = "ZeroMQ core engine in C++, implements ZMTP/3.1"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "LGPL"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/[>=0.1]@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/zeromq/libzmq/archive/v%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.definitions["ZMQ_BUILD_TESTS"] = False
        cmake.definitions["WITH_PERF_TOOL"] = False
        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.cpp", "src")
            self.copy("*.hpp", "src")
