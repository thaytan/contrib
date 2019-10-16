import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class CurlConan(ConanFile):
    name = "curl"
    version = tools.get_env("GIT_TAG", "7.66.0")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    description = "An URL retrieval utility and library"
    generators = "env"

    def build_requirements(self):
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("zlib/[>=1.2.11]@%s/stable" % self.user)
        self.build_requires("openssl/[>=1.1.1b]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://curl.haxx.se/download/curl-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
