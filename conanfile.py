from conans import ConanFile, Meson, tools


def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.5.3"
    except:
        return None

class LibepoxyConan(ConanFile):
    name = "libepoxy"
    version = get_version()
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    description = "Library handling OpenGL function pointer management"
    generators = "env"

    def build_requirements(self):
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        self.build_requires("libx11/[>=1.6.8]@%s/stable" % self.user)
        self.build_requires("mesa/[>=19.2.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/anholt/libepoxy/archive/%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled", "-Dglx=yes", "-Dx11=true", "-Dtests=false"]
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
        meson.install()
