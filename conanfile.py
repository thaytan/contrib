import re
from os import listdir, path, symlink

from conans import ConanFile, tools


class NvJetsonDrivers(ConanFile):
    name = "nv-jetson-drivers"
    version = tools.get_env("GIT_TAG", "32.2.1")
    license = "LGPL"
    description = "NVIDIA built Accelerated GStreamer Plugins"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["public_sources.tbz2"]
    options = {"jetson": ["Nano", "TX2", "Xavier"]}
    default_options = "jetson=TX2"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def source(self):
        if self.options.jetson in ("TX2", "Xavier"):
            tools.get("https://developer.nvidia.com/embedded/dlc/r%s_Release_v1.0/TX2-AGX/Tegra186_Linux_R%s_aarch64.tbz2" % (self.version.replace(".", "-"), self.version))
        elif self.options.jetson == "Nano":
            tools.get("https://developer.nvidia.com/embedded/dlc/r%s_Release_v1.0/Nano-TX1/Tegra210_Linux_R%s_aarch64.tbz2" % (self.version.replace(".", "-"), self.version))
        else:
            raise KeyError("Unknown option: " + self.options.jetson)
        tools.untargz("Linux_for_Tegra/nv_tegra/nvidia_drivers.tbz2", self.source_folder)
        tools.rmdir("Linux_for_Tegra")

    def package(self):
        self.copy("*.so*", dst="lib", keep_path=False, symlinks=False)

        lib_folder = path.join(self.package_folder, "lib")
        with tools.chdir(lib_folder):
            for dl in listdir(lib_folder):
                old = re.search(r".*\.so((\.[0-9]+)+)$", dl)
                new = re.search(r".*\.so", dl)
                if old:
                    symlink(old.group(0), new.group(0))
                    print("Created symlink from " + old.group(0) + " to " + new.group(0))

    def package_info(self):
        self.env_info.JETSON_DRIVER_PATH = path.join(self.package_folder, "lib")
