from conans import *


class OpusConan(ConanFile):
    description = "Modern audio compression for the internet"
    license = "BSD"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "gstreamer"
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
    )

    def source(self):
        tools.get(f"https://archive.mozilla.org/pub/opus/opus-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-shared",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"opus-{self.version}", args)
        autotools.install()
