from build import *
from conans import tools as conantools

# These come from https://developer.nvidia.com/embedded/downloads
download_tx2_url = {
    "32.2.1": "https://developer.nvidia.com/embedded/dlc/r32-2-1_Release_v1.0/TX2-AGX/Tegra186_Linux_R32.2.1_aarch64.tbz2",
    "32.3.1": "https://developer.nvidia.com/embedded/dlc/r32-3-1_Release_v1.0/t186ref_release_aarch64/Tegra186_Linux_R32.3.1_aarch64.tbz2",
}
download_tx1_url = {
    "32.2.1": "https://developer.nvidia.com/embedded/dlc/r32-2-1_Release_v1.0/Nano-TX1/Tegra210_Linux_R32.2.1_aarch64.tbz2",
    "32.3.1": "https://developer.nvidia.com/embedded/dlc/r32-3-1_Release_v1.0/t210ref_release_aarch64/Tegra210_Linux_R32.3.1_aarch64.tbz2",
}


class NvJetsonDrivers(Recipe):
    description = "NVIDIA built Accelerated GStreamer Plugins"
    license = "LGPL"
    exports_sources = ["public_sources.tbz2"]
    options = {"jetson": ["Nano", "TX2", "Xavier"]}
    default_options = "jetson=TX2"

    def source(self):
        if self.options.jetson in ("TX2", "Xavier"):
            self.get(download_tx2_url[self.version])
        elif self.options.jetson == "Nano":
            self.get(download_tx2_url[self.version])
        else:
            raise KeyError("Unknown option: " + self.options.jetson)
        tools.untargz(f"{self.name}-{self.version}.src/nv_tegra/nvidia_drivers.tbz2", self.source_folder)
        conantools.rmdir(f"{self.name}-{self.version}.src")

    def package(self):
        lib_folder = os.path.join(self.package_folder, "lib")

        if self.version in ("32.2.1"):
            self.copy("*.so*", dst="lib", keep_path=False, symlinks=False)

        elif self.version in ("32.3.1"):
            self.copy("*.so*", src="usr/lib/aarch64-linux-gnu/tegra", dst="lib", keep_path=False, symlinks=True)
            # with tools.chdir(lib_folder):
            # symlink("/usr/lib/aarch64-linux-gnu/tegra/libcuda.so", "libcuda.so" )
            self.copy("*.so*", src="usr/lib/aarch64-linux-gnu/tegra-egl", dst="lib", keep_path=False, symlinks=False)
            self.copy("*.so*", src="usr/lib/xorg", dst="lib", keep_path=False, symlinks=False)
        else:
            raise KeyError("Unknown version: " + self.version)

        with tools.chdir(lib_folder):
            for dl in os.listdir(lib_folder):
                old = re.search(r".*\.so((\.[0-9]+)+)$", dl)
                new = re.search(r".*\.so", dl)
                if not old:
                    continue
                if new and os.path.islink(new.group(0)):
                    os.remove(new.group(0))
                os.symlink(old.group(0), new.group(0))
                print("Created symlink from " + old.group(0) + " to " + new.group(0))

    def package_info(self):
        self.env_info.JETSON_DRIVER_PATH = os.path.join(self.package_folder, "lib")
