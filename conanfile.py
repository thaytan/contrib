from conans import ConanFile, Meson, tools


def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.4.99"
    except:
        return None

class LibdrmConan(ConanFile):
    name = "libdrm"
    version = get_version()
    license = "MIT"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Direct Rendering Manager headers and kernel modules"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("libpciaccess/[>=0.14]@%s/stable" % self.user)

    def source(self):
        tools.get("http://dri.freedesktop.org/libdrm/libdrm-%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled", "-Dradeon=false", "-Damdgpu=false", "-Dnouveau=false"]
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
        meson.install()
