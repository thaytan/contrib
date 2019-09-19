from conans import ConanFile, tools, Meson

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "3.1"
    except:
        return None

class GperfConan(ConanFile):
    name = "gperf"
    version = get_version()
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/prozum/conan-libffi"
    license = "https://github.com/libffi/libffi/blob/master/LICENSE"
    description = "A portable, high level programming interface to various calling conventions"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/stable" % self.user)

    def source(self):
        git = tools.Git("%s-%s" % (self.name, self.version))
        git.clone("https://gitlab.com/aivero/public/gperf.git", "meson")

    def build(self):
        meson = Meson(self)
        meson.configure(source_folder="%s-%s" % (self.name, self.version))
        meson.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.srcdirs.append("src")
