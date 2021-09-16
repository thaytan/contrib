from build import *


class GstNnstreamer(GstRecipe):
    description = "Neural Network (NN) Streamer, Stream Processing Paradigm for Neural Network Apps/Devices."
    license = "LGPL"
    build_requires = (
        "cc/[^1.0.0]",
        "meson/[>=0.57.2]",
        "git/[^2.30.0]",
        "flex/[^2.6.4]",
        "bison/[^3.7.2]",
        "tensorflow-lite/[^2.6.0]",
    )

    def requirements(self):
        self.requires(f"gst-plugins-base/[~{self.settings.gstreamer}]")
        self.requires(f"tensorflow-lite/[^2.6.0]")

    def source(self):
        self.get(f"https://github.com/nnstreamer/nnstreamer/archive/refs/tags/v{self.version}.tar.gz")

    def build(self):
        opts = {
            "werror": False,
            "tflite-support": True,
        }
        self.meson(opts)
    
    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy('*.so*', dst='bin', src='lib')
        self.copy('*.a*', dst='bin', src='lib')
