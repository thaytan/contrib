from conans import AutoToolsBuildEnvironment, ConanFile, tools


def conv_version(version):
    version = version.split(".")
    return version[0] + format(version[1], "0<3") + format(version[2], "0<3")


class SqliteConan(ConanFile):
    name = "sqlite"
    version = tools.get_env("GIT_TAG", "3.30.1")
    description = "A C library that implements an SQL database engine"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom:Public Domain"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("tcl/[>=8.6.10]@%s/stable" % self.user)

    def requirements(self):
        self.requires("zlib/[>=1.2.11]@%s/stable" % self.user)
        self.requires("readline/[>=8.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://www.sqlite.org/2019/sqlite-src-%s.zip" %
                  conv_version(self.version))

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-src-%s" %
                         (self.name, conv_version(self.version))):
            self.run("chmod +x configure")
            autotools.configure()
            autotools.install()
