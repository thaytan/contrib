from conans import ConanFile, Meson, tools

import os

class LibNiceConan(ConanFile):
    name = "libnice"
    version = "0.1.15"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "An implementation of the IETF’s Interactive Connectivity Establishment (ICE) standard"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {"gstreamer": [True, False]}
    default_options = "gstreamer=True"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))
        self.requires("glib/2.58.1@%s/%s" % (self.user, self.channel))
        self.requires("openssl/1.1.1b@%s/%s" % (self.user, self.channel))
        if self.options.gstreamer:
            self.requires("gstreamer/1.16.0@%s/%s" % (self.user, self.channel))
            self.requires("gstreamer-plugins-base/1.16.0@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/libnice/libnice/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dgstreamer=" + ("enabled" if self.options.gstreamer else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
        meson.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
