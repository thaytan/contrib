import os

from conans import CMake, ConanFile, tools


class CppzmqConan(ConanFile):
    name = "cppzmq"
    version = tools.get_env("GIT_TAG", "4.3.0")
    description = "ZeroMQ core engine in C++, implements ZMTP/3.1"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    generators ="pkgconf"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libzmq/[>=4.3.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/zeromq/cppzmq/archive/v%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder="%s-%s" % (self.name, self.version))
        cmake.install()

    def package(self):
        os.makedirs(os.path.join(self.package_folder, "lib", "pkgconfig"))
        with open(os.path.join(self.package_folder, "lib", "pkgconfig", "cppzmq.pc"), "w+") as pc_file:
            pc_file.write("prefix=%s\n" % self.package_folder)
            pc_file.write("includedir=${prefix}/include\n")
            pc_file.write("Name: cppzmq\n")
            pc_file.write("Description: ZeroMQ core engine in C++\n")
            pc_file.write("Version: 4.3.0\n")
            pc_file.write("Cflags: -I${includedir}\n")
            pc_file.write("Requires: libzmq\n")
