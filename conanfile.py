from conans import ConanFile, Meson, tools

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.3.0"
    except:
        return None

class LibVaConan(ConanFile):
    name = "libva"
    version = get_version()
    description = "Libva is an implementation for VA-API (VIdeo Acceleration API)"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "x11": [True, False],
        "wayland": [True, False]
    }
    default_options = (
        "x11=True",
        "wayland=False"
    )
    generators = "env"

    def build_requirements(self):
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("libdrm/[>=2.4.96]@%s/stable" % self.user)
        self.requires("libx11/[>=1.6.8]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/intel/libva/archive/%s.tar.gz" % self.version)

    def build(self):
        meson = Meson(self)
        args = ["--auto-features=disabled"]
        args.append("-Dwith_x11=" + ("yes" if self.options.x11 else "no"))
        args.append("-Dwith_wayland=" + ("yes" if self.options.wayland else "no"))
        meson.configure(source_folder="%s-%s" % (self.name, self.version))
        meson.install()
