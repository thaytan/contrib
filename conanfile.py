import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class ItstoolConan(ConanFile):
    name = "itstool"
    version = tools.get_env("GIT_TAG", "2.0.6")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL3"
    description = "XML to PO and back again"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("libxml2/[>=2.9.9]@%s/stable" % self.user)
        self.requires("python/[>=3.7.4]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/itstool/itstool/archive/%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.XDG_DATA_DIRS.append(os.path.join(self.package_folder, "share"))
