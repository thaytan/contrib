import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.util import files


class OpusConan(ConanFile):
    name = "opus"
    version = "1.3.1"
    license = "https://raw.githubusercontent.com/xiph/opus/master/COPYING"
    description = "Modern audio compression for the internet"
    default_user = "bincrafters"
    default_channel = "stable"
    url = "https://github.com/ulricheck/conan-librealsense"
    settings = "os", "compiler", "build_type", "arch"

    def source(self):
        tools.get("https://archive.mozilla.org/pub/opus/opus-%s.tar.gz" % self.version)

    def build(self):
        vars = {
            "CFLAGS": "-fdebug-prefix-map=%s=." % self.source_folder,
            "CXXFLAGS": "-fdebug-prefix-map=%s=." % self.source_folder,
        }
        with tools.environment_append(vars):
            with tools.chdir(os.path.join(self.source_folder, "opus-" + self.version)), tools.environment_append(vars):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.configure()
                autotools.make()
                autotools.make(args=["install"])


    def package(self):
        if self.channel == "testing":
            self.copy("*.cpp", "src")
            self.copy("*.hpp", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        self.cpp_info.srcdirs.append("src")
