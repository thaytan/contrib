from conans import ConanFile, tools


class CMakeConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    license = "custom"
    description = "A cross-platform open-source make system"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def requirements(self):
        self.requires("cc/[>=1.0.0]@%s/stable" % self.user)
        self.requires("pkgconf/[>=1.6.3]@%s/stable" % self.user)
        self.requires("ninja/[>=1.9.0]@%s/stable" % self.user)

    def source(self):
        tools.get(
            "https://github.com/Kitware/CMake/releases/download/v{0}/cmake-{0}.tar.gz".format(
                self.version
            )
        )

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("./bootstrap --prefix=" + self.package_folder)
            self.run("make install")
