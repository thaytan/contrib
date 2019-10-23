import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class NodejsConan(ConanFile):
    name = "nodejs"
    version = tools.get_env("GIT_TAG", "12.13.0")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Evented I/O for V8 javascript"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("python/[>=3.7.4]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("openssl/[>=1.1.1b]@%s/stable" % self.user)
        self.requires("zlib/[>=1.2.11]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/nodejs/node/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = ["--without-npm", "--shared-openssl", "--shared-zlib"]
        with tools.chdir("node-%s" % self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()
