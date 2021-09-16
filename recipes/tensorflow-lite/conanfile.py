from os.path import join
from build import *


BUILD_SUBFOLDER = "tensorflow/lite/tools/make"
C_BUILD_FOLDER = "tensorflow/lite/c"

class TensorflowLite(Recipe):
    name = "tensorflow-lite"
    description = "https://www.tensorflow.org"
    license = "LGPL"
    exports = "tensorflow-lite.pc"
    scm = dict(type="git",
               url="https://github.com/tensorflow/tensorflow.git",
               revision=f"4c0b84bf2a714bcdd18da1f1f94d533d72399d52")

    build_requires = (
        "autotools/[^1.0.0]",
        "cc/[^1.0.0]", 
        "cmake/[^3.18.4]",
        "flatbuffers/[^2.0.0]"
    )

    def requirements(self):
        self.requires(f"flatbuffers/[^2.0.0]")

    def source(self):
        self.run(join(BUILD_SUBFOLDER, "download_dependencies.sh"))

    def build(self):
        with tools.chdir(self.source_folder):
            self.run("cmake tensorflow/lite -DCMAKE_BUILD_TYPE=Debug")
            self.run("cmake --build . -j")
        
    def package(self):
        tools.replace_prefix_in_pc_file("tensorflow-lite.pc", self.package_folder)
        self.copy(pattern="*libtensorflow-lite*", dst="lib", src=f".", keep_path=False)
        self.copy(pattern="*.o", dst="lib", src=f".", keep_path=False)
        self.copy(pattern="*.h", dst="include/tensorflow/lite", src=f"tensorflow/lite", keep_path=True)
        self.copy(pattern="*.c", dst="include/tensorflow/lite", src=f"tensorflow/lite", keep_path=True)
        self.copy(pattern="*.pc", dst="lib/pkgconfig")
        self.copy(pattern="flathash*", dst="bin", src="bin")
        self.copy(pattern="flatc*", dst="bin", src="bin")
        