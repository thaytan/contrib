from conans import AutoToolsBuildEnvironment, ConanFile, tools


class ImagemagickConan(ConanFile):
    name = "imagemagick"
    version = tools.get_env("GIT_TAG", "7.0.9.25")
    tar_version = "%s-%s" % (version[:version.rfind(".")], version[version.rfind(".") + 1:])
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL2"
    description = "An image viewing/manipulation program"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libpng/[>=1.6.37]@%s/stable" % self.user)

    def source(self):
        tools.get("https://imagemagick.org/download/ImageMagick-%s.tar.xz" % self.tar_version)

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("ImageMagick-%s" % self.tar_version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
