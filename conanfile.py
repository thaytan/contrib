from conans import ConanFile, tools, AutoToolsBuildEnvironment

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.2.0"
    except:
        return None

class LibSrtpConan(ConanFile):
    name = "libsrtp"
    version = get_version()
    url = "http://gitlab.com/aivero/public/conan/conan-" + name
    license = "BSD"
    description = "Library for SRTP (Secure Realtime Transport Protocol)"
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/cisco/libsrtp/archive/v%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make(args=["shared_library"])
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")
