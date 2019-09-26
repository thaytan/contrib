from conans import ConanFile, AutoToolsBuildEnvironment, tools
from os import path, remove
from glob import glob

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.0.23"
    except:
        return None

class LibUSBConan(ConanFile):
    name = "libusb"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "LGPL-2.1"
    description = "A cross-platform library to access USB devices"
    settings = "os", "compiler", "build_type", "arch"
    options = {"udev": [True, False]}
    default_options = "udev=False"
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/0.1@%s/stable" % self.user)
        self.build_requires("autotools/1.0.0@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/libusb/libusb/releases/download/v{0}/libusb-{0}.tar.bz2".format(self.version))

    def build(self):
        args = [
            "--disable-static"
        ]
        args.append("--enable-udev" if self.options.udev else "--disable-udev")
        with tools.chdir("%s-%s" % (self.name, self.version)):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.configure(args=args)
                autotools.install()
        for f in glob(path.join(self.package_folder, "**", "*.la"), recursive=True):
            remove(f)

    def package(self):
        if self.settings.build_type == "Debug":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.srcdirs.append("src")
