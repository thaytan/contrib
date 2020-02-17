from conans import ConanFile, Meson, tools


class PixmanConan(ConanFile):
    name = "pixman"
    version = tools.get_env("GIT_TAG", "0.38.4")
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    description = "Image processing and manipulation library"
    license = "custom"
    settings = "os", "arch", "compiler", "build_type"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)

    def source(self):
        tools.get("https://xorg.freedesktop.org/releases/individual/lib/pixman-%s.tar.bz2" % self.version)

    def build(self):
        args = ["--auto-features=disabled"]
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version), args=args)
        meson.install()
