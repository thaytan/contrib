import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class GstreamerNvJetsonEgl(ConanFile):
    name = "gstreamer-nv-jetson-egl"
    version = tools.get_env("GIT_TAG", "32.2.1")
    license = "LGPL"
    description = "NVIDIA jetson egl element"
    url = "https://developer.nvidia.com/embedded/linux-tegra"
    settings = "os", "compiler", "build_type", "arch"
    options = {"jetson": ["Nano", "TX2", "Xavier"]}
    default_options = ("jetson=TX2", )
    generators = "env"
    gst_version = "1.16.0"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("mesa/[>=19.2.0]@%s/stable" % self.user)
        self.requires("nv-jetson-drivers/[>=%s]@%s/stable" % (self.version, self.user))
        self.requires("nv-jetson-v4l2/[>=%s]@%s/stable" % (self.version, self.user))
        self.requires("gstreamer-plugins-base/[>=%s]@%s/stable" % (self.gst_version, self.user))

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

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
