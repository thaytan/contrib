from conans import ConanFile, tools
from os import symlink, path

class JetsonDrivers(ConanFile):
    name = "jetson-drivers"
    version = "32.2.1"
    license = "LGPL"
    description = "NVIDIA built Accelerated GStreamer Plugins"
    url = "https://developer.nvidia.com/embedded/linux-tegra"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources= ["public_sources.tbz2"]
    options = {"jetson": ["Nano", "TX2", "Xavier"]}
    default_options = ("jetson=TX2")
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))

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
