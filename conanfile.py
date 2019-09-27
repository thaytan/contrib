from conans import ConanFile, AutoToolsBuildEnvironment, tools

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "0.4.29"
    except:
        return None

class OrcConan(ConanFile):
    name = "orc"
    version = get_version()
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "LGPL-2.1"
    description = "Optimized Inner Loop Runtime Compiler"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/GStreamer/orc/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-gtk-doc"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
                self.run("./autogen.sh " + " ".join(args))
                autotools = AutoToolsBuildEnvironment(self)
                autotools.configure(args=args)
                autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")
