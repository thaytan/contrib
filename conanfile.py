from conans import AutoToolsBuildEnvironment, ConanFile, tools


class Help2ManConan(ConanFile):
    name = "help2man"
    version = tools.get_env("GIT_TAG", "1.47.11")
    settings = "os", "compiler", "build_type", "arch"
    license = "GPL"
    description = "Conversion tool to create man files"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/help2man/help2man-%s.tar.xz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
