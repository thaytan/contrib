from conans import AutoToolsBuildEnvironment, ConanFile, tools


class ConanWebP(ConanFile):
    name = "webp"
    version = tools.get_env("GIT_TAG", "1.1.0")
    license = "BSD"
    description = "library to encode and decode images in WebP format"
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("make/[>=4.3]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/webmproject/libwebp/archive/v%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("libwebp-%s" % self.version):
            self.run("./autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
