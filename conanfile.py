from conans import ConanFile, tools, AutoToolsBuildEnvironment

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "0.7.0"
    except:
        return None

class CapNProtoConan(ConanFile):
    name = "capnproto"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-zlib"
    license = "MIT"
    description = ("Cap'n Proto serialization/RPC system")
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://capnproto.org/capnproto-c++-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("capnproto-c++-%s" % self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")
