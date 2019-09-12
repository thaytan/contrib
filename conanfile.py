from conans import ConanFile, tools
from os import symlink, path

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "32.2.1"
    except:
        return None

class JetsonDrivers(ConanFile):
    name = "jetson-drivers"
    version = get_version()
    license = "LGPL"
    description = "NVIDIA built Accelerated GStreamer Plugins"
    url = "https://developer.nvidia.com/embedded/linux-tegra"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources= ["public_sources.tbz2"]
    options = {"jetson": ["Nano", "TX2", "Xavier"]}
    default_options = ("jetson=TX2")
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)

    def source(self):
        if self.options.jetson in ("TX2", "Xavier"):
            tools.get("https://developer.nvidia.com/embedded/dlc/r%s_Release_v1.0/TX2-AGX/Tegra186_Linux_R%s_aarch64.tbz2" % (self.version.replace(".", "-"), self.version))
        elif self.options.jetson == "Nano":
            tools.get("https://developer.nvidia.com/embedded/dlc/r%s_Release_v1.0/Nano-TX1/Tegra210_Linux_R%s_aarch64.tbz2" % (self.version.replace(".", "-"), self.version))
        else:
            raise KeyError("Unknown option: " + self.options.jetson)

        tools.untargz("Linux_for_Tegra/nv_tegra/nvidia_drivers.tbz2", self.source_folder)
        tools.rmdir("Linux_for_Tegra")
        for dl in ("nvbufsurface", "nvbuf_utils", "nvbuf_fdmap", "nvdsbufferpool"):
            symlink("lib%s.so.1.0.0" % dl, "lib%s.so" % dl)

    def package(self):
        self.copy("*libnvbuf*.so*", dst="lib", keep_path=False, links=True)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
