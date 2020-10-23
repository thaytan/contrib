from conans import *


class FreetypeConan(ConanFile):
    description = "FreeType is a software library to render fonts"
    license = "GPL2"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    options = {"harfbuzz": [True, False]}
    default_options = ("harfbuzz=True",)
    build_requires = (
        "cc/[^1.0.0]",
        "autotools/[^1.0.0]",
    )
    requires = ("zlib/[^1.2.11]",)

    def requirements(self):
        if self.options.harfbuzz:
            self.requires("harfbuzz/[^2.7.2]")

    def source(self):
        tools.get(f"https://download-mirror.savannah.gnu.org/releases/freetype/freetype-{self.version}.tar.xz")

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"freetype-{self.version}", args)
        autotools.install()
