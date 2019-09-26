from conans import ConanFile, Meson, tools

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.4.4"
    except:
        return None

class JsonGlibBaseConan(ConanFile):
    name = "json-glib"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "A well-groomed and well-maintained collection of GStreamer plugins and elements"
    license = "GPL"
    settings = "os", "arch", "compiler", "build_type"
    options = {"introspection": [True, False]}
    default_options = "introspection=True"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/[>=0.1]@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        self.build_requires("gettext/[>=0.20.1]@%s/stable" % self.user)
        if self.options.introspection:
            self.build_requires("gobject-introspection/[>=1.59.3]@%s/stable" % self.user)

    def requirements(self):
        self.requires("glib/[>=2.62.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://gitlab.gnome.org/GNOME/json-glib/-/archive/{0}/json-glib-{0}.tar.gz".format(self.version))

    def build(self):
        args = ["--auto-features=disabled"]
        args.append("-Dintrospection=" + ("true" if self.options.introspection else "false"))
        meson = Meson(self)
        meson.configure(args=args, source_folder="%s-%s" % (self.name, self.version))
        meson.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")
