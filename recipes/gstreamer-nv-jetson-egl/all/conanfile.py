import os

from conans import *


class GstreamerNvJetsonEgl(ConanFile):
    description = "NVIDIA jetson egl element"
    license = "LGPL"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    options = {"jetson": ["Nano", "TX2", "Xavier"]}
    default_options = ("jetson=TX2",)
    gst_version = "1.16.0"
    build_requires = (
        "generators/1.0.0",
        "gcc/[^7.4.0]",
        "pkgconf/[^1.6.3]",
    )
    requires = (
        "mesa/[^19.2.0]",
        "nv-jetson-drivers/[^%s]" % (self.version),
        "nv-jetson-v4l2/[^%s]" % (self.version),
        "gstreamer-plugins-base/[^%s]" % (self.gst_version),

    def source(self):
        if self.options.jetson in ("TX2", "Xavier"):
            tools.get("https://developer.nvidia.com/embedded/dlc/r%s_Release_v1.0/TX2-AGX/sources/public_sources.tbz2" % self.version.replace(".", "-"))
        elif self.options.jetson == "Nano":
            tools.get("https://developer.nvidia.com/embedded/dlc/r%s_Release_v1.0/Nano-TX1/sources/public_sources.tbz2" % self.version.replace(".", "-"))
        else:
            raise KeyError("Unknown option: " + self.options.jetson)
        tools.untargz("public_sources/gstegl_src.tbz2", self.source_folder)
        tools.rmdir("public_sources")

    def build(self):
        with tools.chdir("gstegl_src/gst-egl"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
        pc_path = os.path.join(self.package_folder, "lib", "pkgconfig", "gstreamer-egl-1.0.pc")
        self.run('sed -i "s/Requires: .*/Requires: gstreamer-1.0 libglvnd x11/" %s' % pc_path)
        self.run('sed -i "s/Libs: .*/Libs: -L\${libdir} -lgstegl-1.0/" %s' % pc_path)
        self.run('sed -i "s/Cflags: .*/Cflags: -I\${includedir}/" %s' % pc_path)
