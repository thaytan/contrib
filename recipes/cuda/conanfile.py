from build import *

driver_map = {
    "10.1.243": "418.87.00",
    "11.1.0": "455.23",
    "11.2.1": "460.32.03",
}


class CudaRecipe(Recipe):
    description = "NVIDIA's GPU programming toolkit"
    license = "Proprietary"
    exports_sources = ("*.pc")
    build_requires = (
        "cc/[^1.0.0]",
        "libxml2/[>=2.9.10]",
    )

    def source(self):
        tools.download(f"https://developer.download.nvidia.com/compute/cuda/{self.version}/local_installers/cuda_{self.version}_{driver_map[self.version]}_linux.run", filename=f"cuda_{self.version}_linux.run")

    def build(self):
        self.run(f'sh cuda_{self.version}_linux.run  --silent --override --override-driver-check --extract="{self.build_folder}"')
        # self.run(f"sh cuda_{self.version}_linux.run  --silent --override --override-driver-check --toolkit --toolkitpath={self.package_folder}")
        os.remove(f"cuda_{self.version}_linux.run")
        self.run(f"sh NVIDIA-Linux-x86_64-{driver_map[self.version]}.run --extract-only")
        os.remove(f"NVIDIA-Linux-x86_64-{driver_map[self.version]}.run")
        self.run("rm -rf libcublas")
        self.run("rm -rf cuda-samples")

    def package(self):
        for toolkit in ("cuda-toolkit", "cuda-toolkit/nvvm"):
            self.copy("*", dst="bin", src=f"{toolkit}/bin")
            self.copy("*", dst="lib", src=f"{toolkit}/lib64")
            self.copy("*", dst="include", src=f"{toolkit}/include")
        self.copy("*.bc", src="cuda-toolkit")
        self.copy("*libcuda.so*", dst="lib", keep_path=False, symlinks=True)
        self.copy("*libnvcuvid.so*", dst="lib", keep_path=False, symlinks=True)
        with tools.chdir(os.path.join(self.package_folder, "lib")):
            os.symlink(f"libnvcuvid.so.{driver_map[self.version]}", "libnvcuvid.so.1")
            os.symlink("libnvcuvid.so.1", "libnvcuvid.so")
        self.copy(pattern="*.pc", dst="lib/pkgconfig")
