from conans import ConanFile, Meson, tools


class GperfConan(ConanFile):
    name = "gperf"
    version = tools.get_env("GIT_TAG", "3.1")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/prozum/conan-libffi"
    license = "GPL3"
    description = "A portable, high level programming interface to various calling conventions"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)

    def source(self):
        git = tools.Git("%s-%s" % (self.name, self.version))
        git.clone("https://gitlab.com/aivero/public/gperf.git", "meson")

    def build(self):
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version))
        meson.install()
