import os

from conans import *


class ImagemagickConan(ConanFile):
    description = "An image viewing/manipulation program"
    license = "GPL2"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("autotools/[^1.0.0]",)
    requires = (
        "base/[^1.0.0]",
        "libpng/[^1.6.37]",
    )

    def source(self):
        tar_version = "-".join([self.version[: self.version.rfind(".")], self.version[self.version.rfind(".") + 1 :]])
        tools.get(f"https://github.com/ImageMagick/ImageMagick/archive/{tar_version}.tar.gz")

    def build(self):
        args = ["--disable-static", "--disable-dependency-tracking"]
        with tools.chdir(f"ImageMagick-{self.tar_version}"):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.MAGICK_CONFIGURE_PATH = os.path.join(self.package_folder, "etc", "ImageMagick-" + self.version.split(".")[0])
