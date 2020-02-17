from conans import ConanFile, Meson, tools


class FribidiConan(ConanFile):
    name = "fribidi"
    version = tools.get_env("GIT_TAG", "1.0.5")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "The Free Implementation of the Unicode Bidirectional Algorithm"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.5.12]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/fribidi/fribidi/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = ["--auto-features=disabled", "-Ddocs=false"]
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
        meson.install()
