import os

from conans import ConanFile, tools


class GstreamerNvJetsonV4l2(ConanFile):
    name = "gstreamer-nv-jetson-v4l2"
    version = tools.get_env("GIT_TAG", "32.2.1")
    license = "LGPL"
    description = "NVIDIA jetson v4l2 element"
    settings = "os", "compiler", "build_type", "arch"
    options = {"jetson": ["Nano", "TX2", "Xavier"]}
    default_options = ("jetson=TX2", )
    gst_version = "1.16.0"
    exports_sources = {"patches/*"}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("nv-jetson-drivers/[>=%s]@%s/stable" % (self.version, self.user))
        self.requires("nv-jetson-v4l2/[>=%s]@%s/stable" % (self.version, self.user))
        self.requires("gstreamer-plugins-base/[>=%s]@%s/stable" % (self.gst_version, self.user))
        self.requires("libglvnd/[>=1.2.0]@%s/stable" % (self.user))

    def source(self):
        if self.options.jetson in ("TX2", "Xavier"):
            tools.get("https://developer.nvidia.com/embedded/dlc/r%s_Release_v1.0/TX2-AGX/sources/public_sources.tbz2" % self.version.replace(".", "-"))
        elif self.options.jetson == "Nano":
            tools.get("https://developer.nvidia.com/embedded/dlc/r%s_Release_v1.0/Nano-TX1/sources/public_sources.tbz2" % self.version.replace(".", "-"))
        else:
            raise KeyError("Unknown option: " + self.options.jetson)
        tools.untargz("public_sources/gst-nvvideo4linux2_src.tbz2", self.source_folder)
        tools.rmdir("public_sources")
        tools.patch(patch_file="patches/gstv4l2.c.patch")
        tools.patch(patch_file="patches/gstv4l2videoenc.c.patch")

    def build(self):
        env = {"LIB_INSTALL_DIR": os.path.join(self.deps_cpp_info["nv-jetson-drivers"].rootpath, "lib")}
        with tools.chdir("gst-v4l2"), tools.environment_append(env):
            self.run("make")

    def package(self):
        self.copy("*.so*", dst="lib/gstreamer-1.0", keep_path=False)

    def package_info(self):
        self.env_info.GST_PLUGIN_PATH.append(os.path.join(self.package_folder, "lib", "gstreamer-1.0"))
