from build import *


class FFMpegRecipe(Recipe):
    description = "A complete, cross-platform solution to record, convert and stream audio and video"
    license = "LGPL"
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

        # intended for rpi 64-bit build, may need alternate implementation
        if self.settings.arch == "armv8":
            args += ["--enable-gpl", "--enable-nonfree", "--arch=aarch64"]
            #args += ["--enable-libfreetype", "--enable-libopus"]
            #args += ["--enable-libwebp", "--enable-libdrm"]
            #args += ["--enable-libaom", "--enable-libass", "--enable-libxml2"]
            #args += ["--enable-libfdk-aac", "--enable-libmp3lame", "--enable-libvorbis"]
            #args += ["--enable-libx264", "--enable-libx265", "--enable-libvpx"]

        self.autotools(args)
