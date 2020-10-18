from conans import *


class DbusConan(ConanFile):
    description = "Freedesktop.org message bus system"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/[^1.0.0]",
        "autoconf-archive/[^2019.01.06]",
    )
    requires = (
        "base/[^1.0.0]",
        "expat/[^2.2.7]",
    )

    def source(self):
        tools.get(f"https://gitlab.freedesktop.org/dbus/dbus/-/archive/dbus-{self.version}/dbus-dbus-{self.version}.tar.bz2")

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("dbus-dbus-" + self.version):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
