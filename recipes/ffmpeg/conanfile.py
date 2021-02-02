from build import *


class FFMpegRecipe(Recipe):
    description = "A complete, cross-platform solution to record, convert and stream audio and video"
    license = "GPL"
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
        self.autotools(args)
