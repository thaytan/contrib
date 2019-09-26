from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.17.2"
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

    def build_requirements(self):
        self.build_requires("env-generator/[>=0.1]@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)
        if self.options.introspection:
            self.build_requires("gobject-introspection/[>=1.59.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)
        self.requires("pixman/[>=0.38.4]@%s/stable" % self.user)
        self.requires("freetype/[>=2.10.1]@%s/stable" % self.user)
        self.requires("fontconfig/[>=2.13.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://gitlab.freedesktop.org/cairo/cairo/-/archive/{0}/cairo-{0}.tar.gz".format(self.version))

    def build(self):
        args = [
            "--disable-static"
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
        self.env_info.GI_TYPELIB_PATH.append(os.path.join(self.package_folder, "lib", "girepository-1.0"))
