import os

from conans import *

mapper = {
    "TX2": "T186",
    "Xaviar": "T186",
    "Nano": "T210",
}


class GstreamerNvJetsonV4l2(ConanFile):
    description = "NVIDIA jetson v4l2 element"
    license = "LGPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    options = {"jetson": ["Nano", "TX2", "Xavier"]}
    default_options = ("jetson=TX2",)
    gst_version = "1.16.0"
    exports_sources = {"patches/*"}
    build_requires = (
        "cc/[^1.0.0]",
        "pkgconf/[^1.6.3]",
    )

    def requirements(self):
        self.requires(f"nv-jetson-drivers/[^{self.version}]")
        self.requires(f"nv-jetson-v4l2/[^{self.version}]")
        self.requires(f"gstreamer-plugins-base/[^{self.gst_version}]")
        self.requires("libglvnd/[^1.2.0]")

    def source(self):
        tools.get(f"https://developer.nvidia.com/embedded/dlc/r{self.version.replace('.', '-')}_Release_v1.0/Sources/{mapper[str(self.options.jetson)]}/public_sources.tbz2")
        tools.untargz("Linux_for_Tegra/source/public/gst-nvvideo4linux2_src.tbz2", self.source_folder)
        tools.rmdir("public_sources")
        tools.patch(patch_file="patches/Makefile.patch")
        tools.patch(patch_file="patches/gstv4l2.c.patch")

    def build(self):
        env = {"LIB_INSTALL_DIR": os.path.join(self.deps_cpp_info["nv-jetson-drivers"].rootpath, "lib")}
        with tools.chdir("gst-v4l2"), tools.environment_append(env):
            self.run("make")

    def package(self):
        self.copy("*.so*", dst="lib/gstreamer-1.0", keep_path=False)
