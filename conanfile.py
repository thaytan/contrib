from conans import ConanFile, tools
from os import path

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "32.2.1"
    except:
        return None

class GstreamerNvV4l2(ConanFile):
    name = "gstreamer-nv-v4l2"
    version = get_version()
    license = "LGPL"
    description = "NVIDIA built Accelerated GStreamer Plugins"
    url = "https://developer.nvidia.com/embedded/linux-tegra"
    settings = "os", "compiler", "build_type", "arch"
    options = {"jetson": ["Nano", "TX2", "Xavier"]}
    default_options = ("jetson=TX2",)
    generators = "env"
    gst_version = "1.16.0"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)
        self.requires("nv-v4l2/%s@%s/stable" % (self.version, self.user))
        self.requires("jetson-drivers/%s@%s/stable" % (self.version, self.user))
        self.requires("gstreamer/%s@%s/stable" % (self.gst_version, self.user))
        self.requires("gstreamer-plugins-base/%s@%s/stable" % (self.gst_version, self.user))
        self.requires("deepstream/4.0@%s/stable" % self.user)

    def source(self):
        if self.options.jetson in ("TX2", "Xavier"):
            tools.get("https://developer.nvidia.com/embedded/dlc/r%s_Release_v1.0/TX2-AGX/sources/public_sources.tbz2" % self.version.replace(".", "-"))
        elif self.options.jetson == "Nano":
            tools.get("https://developer.nvidia.com/embedded/dlc/r%s_Release_v1.0/Nano-TX1/sources/public_sources.tbz2" % self.version.replace(".", "-"))
        else:
            raise KeyError( "Unknown option: " + self.options.jetson)

        tools.untargz("public_sources/gst-nvvideo4linux2_src.tbz2", self.source_folder)
        tools.rmdir("public_sources")

    def build(self):
        env = {
            "LIB_INSTALL_DIR": path.join(self.deps_cpp_info["jetson-drivers"].rootpath, "lib")
        }
        with tools.chdir("gst-v4l2"), tools.environment_append(env):
            self.run("make")

    def package(self):
        self.copy("*.so*", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.GST_PLUGIN_PATH.append(path.join(self.package_folder, "lib", "gstreamer-1.0"))
