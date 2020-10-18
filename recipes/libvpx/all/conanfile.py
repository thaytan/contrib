from conans import *


class LibVpxConan(ConanFile):
    description = "WebM VP8/VP9 Codec SDK"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "gcc/7.4.0",
        "yasm/[^1.3.0]",
    )

    def source(self):
        tools.get(f"https://github.com/webmproject/libvpx/archive/v{self.version}.tar.gz")

    def build(self):
        args = [
            "--enable-shared",
            "--disable-static",
            "--disable-install-docs",
            "--disable-install-srcs",
        ]
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
