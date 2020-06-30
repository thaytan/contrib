from conans import AutoToolsBuildEnvironment, ConanFile, tools


class CapNProtoConan(ConanFile):
    name = "capnproto"
    version = tools.get_env("GIT_TAG", "0.7.0")
    license = "MIT"
    description = "Cap'n Proto serialization/RPC system"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def source(self):
        tools.get("https://capnproto.org/capnproto-c++-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("capnproto-c++-%s" % self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()
