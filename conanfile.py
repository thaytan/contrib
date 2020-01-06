from conans import ConanFile, AutoToolsBuildEnvironment, tools

class OrcConan(ConanFile):
    name = "orc"
    version = tools.get_env("GIT_TAG", "0.4.31")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "LGPL-2.1"
    description = "Optimized Inner Loop Runtime Compiler"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)

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
