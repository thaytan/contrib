import os
from glob import glob

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class FontconfigConan(ConanFile):
    name = "fontconfig"
    version = tools.get_env("GIT_TAG", "2.13.92")
    license = "Old MIT"
    description = "A library for configuring and customizing font access"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    generators ="pkgconf"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("gperf/[>=3.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("freetype/[>=2.10.1]@%s/stable" % self.user)
        self.requires("libuuid/[>=1.0.3]@%s/stable" % self.user)
        self.requires("expat/[>=2.2.7]@%s/stable" % self.user)

    def source(self):
        tools.get("https://gitlab.freedesktop.org/fontconfig/fontconfig/-/archive/{0}/fontconfig-{0}.tar.gz".format(self.version))

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()

    def package(self):
        with tools.chdir(self.package_folder + "/etc/fonts/conf.d"):
            for root, dirs, files in os.walk("."):
                for filename in files:
                    os.remove(filename)

        with tools.chdir(self.package_folder + "/etc/fonts/conf.d"):
            for root, dirs, files in os.walk(self.package_folder + "/share/fontconfig/conf.avail"):
                for filename in files:
                    os.symlink("../../../share/fontconfig/conf.avail/" + filename, filename)

    def package_info(self):
        self.env_info.FONTCONFIG_PATH.append(os.path.join(self.package_folder, "etc", "fonts"))
