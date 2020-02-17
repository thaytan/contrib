from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibVpxConan(ConanFile):
    name = "libvpx"
    version = tools.get_env("GIT_TAG", "1.8.0")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "WebM VP8/VP9 Codec SDK"
    license = "BSD"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/7.4.0@%s/stable" % self.user)
        self.build_requires("yasm/[>=1.3.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/webmproject/libvpx/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = ["--enable-shared", "--disable-static", "--disable-install-docs", "--disable-install-srcs"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
