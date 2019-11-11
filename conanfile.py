from conans import AutoToolsBuildEnvironment, ConanFile, tools


class SharedMimeInfoConan(ConanFile):
    name = "shared-mime-info"
    version = tools.get_env("GIT_TAG", "1.14")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL2"
    description = "Freedesktop.org Shared MIME Info"
    generators = "env"

    def build_requirements(self):
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("itstool/[>=2.0.6]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)
        self.requires("libxml2/[>=2.9.9]@%s/stable" % self.user)

    def source(self):
        tools.get("https://gitlab.freedesktop.org/xdg/shared-mime-info/-/archive/Release-{0}/shared-mime-info-Release-{0}.tar.bz2".format(self.version.replace(".", "-")))

    def build(self):
        args = ["--disable-update-mimedb"]
        with tools.chdir("%s-Release-%s" % (self.name, self.version.replace(".", "-"))):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
