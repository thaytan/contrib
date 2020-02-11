from conans import AutoToolsBuildEnvironment, ConanFile, tools


class DbusConan(ConanFile):
    name = "dbus"
    version = tools.get_env("GIT_TAG", "1.12.16")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL"
    description = "Freedesktop.org message bus system"
    generators ="pkgconf"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("autoconf-archive/[>=2019.01.06]@%s/stable" % self.user)

    def requirements(self):
        self.requires("expat/[>=2.2.7]@%s/stable" % self.user)

    def source(self):
        tools.get("https://gitlab.freedesktop.org/dbus/dbus/-/archive/dbus-{0}/dbus-dbus-{0}.tar.bz2".format(self.version))

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("dbus-dbus-" + self.version):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
