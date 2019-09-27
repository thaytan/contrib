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
    generators = "env"

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("libdrm/[>=2.4.96]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/intel/libva/archive/%s.tar.gz" % self.version)

    def build(self):
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version))
        meson.install()
