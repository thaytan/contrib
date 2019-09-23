from conans import ConanFile, AutoToolsBuildEnvironment, tools

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "0.14"
    except:
        return None

class LibPciAccessConan(ConanFile):
    name = "libpciaccess"
    version = get_version()
    description = "Generic PCI access library"
    url = "https://gitlab.com/aivero/public/conan/conan-libusb"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires("xorg-util-macros/1.19.1@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/freedesktop/xorg-libpciaccess/archive/libpciaccess-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("xorg-libpciaccess-libpciaccess-" + self.version):
            self.run("autoreconf -i")
            autotools.configure(args=args)
            autotools.install()

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
