from conans import ConanFile, Meson, tools

import os

class LibNiceConan(ConanFile):
    name = "libnice"
    version = "0.1.15"
    default_user = "bincrafters"
    default_channel = "stable"
    url = "https://github.com/bincrafters/conan-" + name
    description = "An implementation of the IETF’s Interactive Connectivity Establishment (ICE) standard"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "gstreamer": [True, False],
    }
    default_options = (
        "gstreamer=True",
    )

    def configure(self):
        pass

    def requirements(self):
        self.requires("glib/2.58.1@%s/%s" % (self.user, self.channel))
        if self.options.gstreamer:
            self.requires("gstreamer/1.15.1@%s/%s" % (self.user, self.channel))
            self.requires("gstreamer-plugins-base/1.15.1@%s/%s" % (self.user, self.channel))

    def source(self):
        tools.get("https://github.com/libnice/libnice/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dgstreamer=" + ("enabled" if self.options.gstreamer else "disabled"))
        meson = Meson(self)
        meson.configure(source_folder="libnice-" + self.version, args=args, pkg_config_paths=os.environ["PKG_CONFIG_PATH"].split(":"))
        meson.build()
        meson.install()

    def package(self):
        if self.channel == "testing":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
