from conans import ConanFile, Meson, tools

import os

class GStreamerVaapiConan(ConanFile):
    name = "gstreamer-vaapi"
    version = "master"
    url = "https://github.com/bincrafters/conan-" + name
    description = "Hardware-accelerated video decoding, encoding and processing on Intel graphics through VA-API"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {}
    default_options = ()
    requires = (
        "glib/2.58.1@bincrafters/stable",
        "gstreamer/%s@bincrafters/stable" % version,
        "gstreamer-plugins-base/%s@bincrafters/stable" % version,
        "gstreamer-plugins-bad/%s@bincrafters/stable" % version,
    )

    def source(self):
        tools.get("https://github.com/GStreamer/gstreamer-vaapi/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--default-library=shared", "--libdir=lib", "-Dintrospection=disabled", "-Dexamples=disabled", "-Dtests=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="gstreamer-vaapi-" + self.version, args=args, pkg_config_paths=os.environ['PKG_CONFIG_PATH'].split(":"))
        meson.build()
        meson.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gsteamer-1.0"))
