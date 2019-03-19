import os
from conans import ConanFile, CMake, tools
from conans.util import files


class LibzmqConan(ConanFile):
    name = "libzmq"
    version = "4.3.1"
    license = "https://raw.githubusercontent.com/zeromq/libzmq/master/COPYING"
    description = "ZeroMQ core engine in C++, implements ZMTP/3.1"
    default_user = "bincrafters"
    default_channel = "stable"
    url = "https://github.com/bincrafters/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    def requirements(self):
        pass
        #self.requires("libusb/1.0.22@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/zeromq/libzmq/archive/v%s.tar.gz" % self.version)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = ("ON" if self.options.shared else "OFF")
        cmake.definitions['ZMQ_BUILD_TESTS'] = False
        cmake.definitions['WITH_PERF_TOOL'] = False
        vars = {
            "CFLAGS": "-fdebug-prefix-map=%s=." % self.source_folder,
            "CXXFLAGS": "-fdebug-prefix-map=%s=." % self.source_folder,
        }
        with tools.environment_append(vars):
            cmake.configure(source_folder=self.name + "-" + self.version)
            cmake.build()
            cmake.install()

    def package(self):
        if self.channel == "testing":
            self.copy("*.cpp", "src")
            self.copy("*.hpp", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        self.cpp_info.srcdirs.append("src")
