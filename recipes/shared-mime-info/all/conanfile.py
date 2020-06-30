from conans import AutoToolsBuildEnvironment, ConanFile, tools


class SharedMimeInfoConan\(ConanFile\):
    description = "Freedesktop.org Shared MIME Info"
    license = "GPL2"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("itstool/[>=2.0.6]@%s/stable" % self.user)
        self.build_requires("xz/[>=5.2.4]@%s/stable" % self.user)

    def requirements(self):
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
