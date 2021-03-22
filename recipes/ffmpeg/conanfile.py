from build import *


class FFMpegRecipe(Recipe):
    description = "A complete, cross-platform solution to record, convert and stream audio and video"
    license = "LGPL"
    settings = Recipe.settings + ("hardware",)

    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
        "yasm/[^1.3.0]",
    )

    def source(self):
        self.get(f"http://ffmpeg.org/releases/ffmpeg-{self.version}.tar.bz2")

    def build(self):
        args = [
            "--disable-doc",
            "--disable-programs",
            "--cc=cc",
            "--cxx=c++",
        ]

        # additional args for rpi.4 64-bit
        if self.settings.hardware == "rpi":
            if self.settings.arch == "armv8":
                args += ["--enable-nonfree", "--arch=aarch64"]

        self.autotools(args)
