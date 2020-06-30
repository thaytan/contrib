import os

from conans import *


class ImagemagickConan(ConanFile):
    description = "An image viewing/manipulation program"
    license = "GPL2"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}
    build_requires = (
        "generators/1.0.0",
        "autotools/[^1.0.0]",
    )
    requires = ("libpng/[^1.6.37]",)

    def source(self):
        tar_version = "%s-%s" % (self.version[: self.version.rfind(".")], self.version[self.version.rfind(".") + 1 :],)
        tools.get("https://github.com/ImageMagick/ImageMagick/archive/%s.tar.gz" % tar_version)

    def build(self):
        args = ["--disable-static", "--disable-dependency-tracking"]
        with tools.chdir("ImageMagick-%s" % self.tar_version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.MAGICK_CONFIGURE_PATH = os.path.join(self.package_folder, "etc", "ImageMagick-" + self.version.split(".")[0])
