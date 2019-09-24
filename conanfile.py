from conans import ConanFile, tools, AutoToolsBuildEnvironment

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.4.18"
    except:
        return None

class M4Conan(ConanFile):
    name = "m4"
    version = get_version()
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "GPL3"
    description = "The GNU macro processor"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/m4/m4-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.srcdirs.append("src")
