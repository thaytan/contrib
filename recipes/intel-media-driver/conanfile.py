from build import *


class IntelMediaDriverRecipe(Recipe):
    description = "Intel Media Driver for VAAPI Broadwell iGPUs"
    license = "MIT"
    build_requires = ("cc/[^1.0.0]", "cmake/[^3.18.4]")
    requires = (
        "intel-gmmlib/[^20.3.2]",
        "libva/[^2.9.0]",
        "libpciaccess/[^0.16]",
    )

    def source(self):
        self.get(f"https://github.com/intel/media-driver/archive/intel-media-{self.version}.tar.gz")

    def build(self):
        os.environ["CPATH"] += ":" + ":".join(self.deps_cpp_info["libx11"].include_paths + self.deps_cpp_info["xorgproto"].include_paths)
        self.cmake()
