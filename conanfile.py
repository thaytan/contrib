from conans import ConanFile, AutoToolsBuildEnvironment, tools

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.13.1"
    except:
        return None

class FontconfigConan(ConanFile):
    name = "fontconfig"
    version = get_version()
    license = "Old MIT"
    description = "A library for configuring and customizing font access"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)
        self.requires("freetype/2.10.1@%s/stable" % self.user)
        self.requires("gperf/3.1@%s/stable" % self.user)

    def build_requirements(self):
        self.build_requires("gettext/0.20.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://gitlab.freedesktop.org/fontconfig/fontconfig/-/archive/{0}/fontconfig-{0}.tar.gz".format(self.version))

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name , self.version)):
            self.run("./autogen.sh")
            autotools.configure()
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
