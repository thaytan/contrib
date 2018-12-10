from conans import ConanFile, Meson, tools

import os

class GStreamerConan(ConanFile):
    name = "gstreamer-1.0"
    version = "1.14.4"
    url = "https://github.com/bincrafters/conan-" + name
    homepage = "https://github.com/GStreamer/gstreamer"
    description = "A framework for streaming media"
    license = "https://gitlab.freedesktop.org/gstreamer/gstreamer/raw/master/COPYING"
    settings = "os", "arch", "compiler", "build_type"
    options = {}
    default_options = ()
    requires = (
        "glib-2.0/2.58.1@bincrafters/stable",
        "gobject-2.0/2.58.1@bincrafters/stable",
        "gmodule-2.0/2.58.1@bincrafters/stable",
        "gio-2.0/2.58.1@bincrafters/stable",
        "gio-unix-2.0/2.58.1@bincrafters/stable",
    )
    source_subfolder = "source"
    build_subfolder = "build"
    generators = "pkg_config"
    args = ['--default-library=shared', '-Ddisable_introspection=True']
    lib_targets = [
        ("gstreamer-1.0", ["gst"]),
    ]
    custom_targets = [
    ]

    def source(self):
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version))
        os.rename("gstreamer-" + self.version, self.source_subfolder)

    def _configure_meson(self):
        meson = Meson(self)
        meson.configure(source_folder=self.source_subfolder, build_folder=self.build_subfolder, args=self.args)
        return meson

    def _lib_name(self, lib):
        return "lib%s.so.0.%s0%s.0" % (lib[0], self.version.split(".")[1], self.version.split(".")[2])

    def _lib_path(self, lib):
        return os.path.join(os.path.join(*lib[1]), self._lib_name(lib))

    def build(self):
        self.meson = self._configure_meson()
        targets = list(map(self._lib_path, self.lib_targets))
        targets += self.custom_targets
        self.meson.build(build_dir=self.build_subfolder, targets=targets)

    def package(self):
        for target in self.lib_targets + self.custom_targets:
            self.copy("*lib" + target[0] + ".so*", dst="lib", keep_path=False, symlinks=True)
        self.copy("*.h", dst="include/gst",
                  src=self.source_subfolder + "/gst")
        self.copy("*.h", dst="include/gst",
                  src=self.build_subfolder + "/gst",
                  keep_path=False)
        #self.copy("gstenumtypes.h", dst="include/gst",
        #          src=self.build_subfolder + "/gst",
        #          keep_path=False)
        #self.copy("gstconfig.h", dst="include/gst",
        #          src=self.build_subfolder + "/gst",
        #          keep_path=False)
        #self.copy("gstversion.h", dst="include/gst",
        #          src=self.build_subfolder + "/gst",
        #          keep_path=False)

        #self.copy("*.lib", dst="lib", keep_path=False)
        #self.copy("*.dll", dst="bin", keep_path=False)
        #self.copy("*.dylib*", dst="lib", keep_path=False)
        #self.copy("*.so", dst="lib", keep_path=False)
        #self.copy("*.so", dst="lib", src="libs/gst", keep_path=False)
        #self.copy("*.so", dst="lib", src="gst", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["gstreamer-1.0"]
