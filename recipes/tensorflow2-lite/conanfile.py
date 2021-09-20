from os.path import join
from build import *


BUILD_SUBFOLDER = f"tensorflow/lite/tools/make"

class Tensorflow2Lite(Recipe):
    name = "tensorflow2-lite"
    description = "https://www.tensorflow.org"
    license = "LGPL"
    exports = "tensorflow2-lite.pc"

    build_requires = (
        "autotools/[^1.0.0]",
        "cc/[^1.0.0]", 
        "cmake/[^3.18.4]",
        "flatbuffers/[^2.0.0]"
    )

    def requirements(self):
        self.requires(f"flatbuffers/[^2.0.0]")

    def source(self):
        self.get(f"https://github.com/tensorflow/tensorflow/archive/refs/tags/v{self.version}.tar.gz")
        self.run(join(self.src, BUILD_SUBFOLDER, "download_dependencies.sh"))

    def build(self):
        self.cmake(source_folder=os.path.join(self.src, "tensorflow/lite"))

    def package(self):
        # Pkg-config files
        tools.replace_prefix_in_pc_file("tensorflow2-lite.pc", self.package_folder)
        self.copy(pattern="*.pc", dst="lib/pkgconfig")
        self.copy(pattern="*.so", dst="lib", src=f".", keep_path=False)
        self.copy(pattern="*.h", dst="include/tensorflow/lite", src=join(self.src, "tensorflow/lite"), keep_path=True)
       