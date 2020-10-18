from conans import *


class FFMpegConan(ConanFile):
    description = "A complete, cross-platform solution to record, convert and stream audio and video"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
        "yasm/[^1.3.0]",
    )

    def source(self):
        tools.get(f"http://ffmpeg.org/releases/ffmpeg-{self.version}.tar.bz2")

    def build(self):
        args = [
            "--disable-shared",
            "--enable-static",
            "--disable-doc",
            "--disable-programs",
            "--cc=cc",
            "--cxx=c++",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"ffmpeg-{self.version}", args)
        autotools.make()
        autotools.install()
