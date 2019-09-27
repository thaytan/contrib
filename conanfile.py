from conans import ConanFile, Meson, tools

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.0.5"
    except:
        return None

class FribidiConan(ConanFile):
    name = "fribidi"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "The Free Implementation of the Unicode Bidirectional Algorithm"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/fribidi/fribidi/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled", "-Ddocs=false"]
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
        meson.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")
