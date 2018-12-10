from conans import ConanFile, Meson, tools

import os

class GStreamerPluginsBaseConan(ConanFile):
    name = "gstreamer-plugins-base-1.0"
    version = "1.14.4"
    url = "https://github.com/bincrafters/conan-" + name
    description = "A well-groomed and well-maintained collection of GStreamer plugins and elements"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {}
    default_options = ()
    requires = (
        "glib-2.0/2.58.1@bincrafters/stable",
        "gobject-2.0/2.58.1@bincrafters/stable",
        "gmodule-2.0/2.58.1@bincrafters/stable",
        "gmodule-no-export-2.0/2.58.1@bincrafters/stable",
        "gio-2.0/2.58.1@bincrafters/stable",
        "gio-unix-2.0/2.58.1@bincrafters/stable",
        "gstreamer-1.0/%s@bincrafters/stable" % version,
        "gstreamer-base-1.0/%s@bincrafters/stable" % version,
        "gstreamer-net-1.0/%s@bincrafters/stable" % version,
        "gstreamer-check-1.0/%s@bincrafters/stable" % version,
        "gstreamer-controller-1.0/%s@bincrafters/stable" % version,
    )
    source_subfolder = "source"
    build_subfolder = "build"
    generators = "pkg_config"
    args = ["-Dlibrary_format=shared", "-Ddisable_introspection=true", "-Ddisable_examples=true"]
    lib_targets = []
    custom_targets = []
    deps = []

    def source(self):
        source_url = "https://gstreamer.freedesktop.org/src/gst-plugins-base/gst-plugins-base-%s.tar.xz" % self.version
        tools.get(source_url)
        extracted_dir = "gst-plugins-base-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def _configure_meson(self):
        meson = Meson(self)
        meson.configure(source_folder=self.source_subfolder, build_folder=self.build_subfolder, args=self.args)
        return meson

    def _lib_name(self, lib):
        return "lib%s.so.0.%s0%s.0" % (lib[0], self.version.split(".")[1], self.version.split(".")[2])

    def _lib_path(self, lib):
        return "gst-libs/gst/" + lib[1] + "/" + self._lib_name(lib)

    def build(self):
        self.meson = self._configure_meson()
        if self.name == "gstreamer-plugins-base-1.0":
            self.meson.build(build_dir=self.build_subfolder)
        targets = list(map(self._lib_path, self.lib_targets))
        targets += self.custom_targets
        if len(targets) > 0:
            self.meson.build(build_dir=self.build_subfolder, targets=targets)

    def package(self):
        if self.name == "gstreamer-plugins-base-1.0":
                self.copy("*.h",
                          dst="include/gst/",
                          src=self.source_subfolder + "/gst-libs/gst/")
                self.copy("*.h",
                          dst="include/gst/",
                          src=self.build_subfolder + "/gst-libs/gst/")
        for target in self.lib_targets:
            self.copy("*lib" + target[0] + ".so*", dst="lib", keep_path=False)

    def package_info(self):
        for target in self.lib_targets:
            self.cpp_info.libs = [target[0]]
        self.cpp_info.public_deps = ["gstreamer-1.0", "gstreamer-base-1.0"] + self.deps
        if self.name != "gstreamer-plugins-base-1.0":
            self.cpp_info.public_deps += ["gstreamer-plugins-base-1.0"]
