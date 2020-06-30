import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class ImagemagickConan(ConanFile):
    tar_version = "%s-%s" % (
        version[: version.rfind(".")],
        version[version.rfind(".") + 1 :],
    )
    settings = "os", "compiler", "build_type", "arch"
    license = "GPL2"
    description = "An image viewing/manipulation program"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libpng/[>=1.6.37]@%s/stable" % self.user)

    def source(self):
        tools.get(
            "https://github.com/ImageMagick/ImageMagick/archive/%s.tar.gz"
            % self.tar_version
        )

    def build(self):
        args = ["--disable-static", "--disable-dependency-tracking"]
        with tools.chdir("ImageMagick-%s" % self.tar_version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.MAGICK_CONFIGURE_PATH = os.path.join(
            self.package_folder, "etc", "ImageMagick-" + self.version.split(".")[0]
        )
