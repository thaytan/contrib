from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "4.3.0"
    except:
        return None

class CairoConan(ConanFile):
    name = "cairo"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "2D graphics library with support for multiple output devices"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    options = {"introspection": [True, False]}
    default_options = ("introspection=True")
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))
        self.requires("glib/2.58.1@%s/%s" % (self.user, self.channel))
        self.requires("pixman/0.38.4@%s/%s" % (self.user, self.channel))
        self.requires("freetype/2.10.1@%s/%s" % (self.user, self.channel))
        if self.options.introspection:
            self.requires("gobject-introspection/1.59.3@%s/%s" % (self.user, self.channel),)

    def source(self):
        tools.get("https://gitlab.freedesktop.org/cairo/cairo/-/archive/{0}/cairo-{0}.tar.gz".format(self.version))

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
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
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
