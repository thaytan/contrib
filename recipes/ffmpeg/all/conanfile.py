from conans import *


class FFMpegConan(ConanFile):
    description = "A complete, cross-platform solution to record, convert and stream audio and video"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("yasm/[^1.3.0]",)

    def source(self):
        tools.get(f"http://ffmpeg.org/releases/ffmpeg-{self.version}.tar.bz2")

    def build(self):
        args = [
            "--disable-static",
            "--enable-shared",
            "--disable-doc",
            "--disable-programs",
        ]
        if self.settings.build_type == "Debug":
            args.extend(
                ["--disable-optimizations", "--disable-mmx", "--disable-stripping", "--enable-debug",]
            )
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
