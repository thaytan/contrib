from conans import ConanFile, tools, AutoToolsBuildEnvironment

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.8.0"
    except:
        return None

class LibVpxConan(ConanFile):
    name = "libvpx"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "WebM VP8/VP9 Codec SDK"
    license = "BSD"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("yasm/[>=1.3.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/webmproject/libvpx/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = []
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")
