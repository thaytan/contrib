from conans import *


class DbusConan(ConanFile):
    description = "Freedesktop.org message bus system"
    license = "GPL"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/[^1.0.0]",
        "autoconf-archive/[^2019.01.06]",
    )
    requires = ("expat/[^2.2.7]",)

    def source(self):
        tools.get(f"https://gitlab.freedesktop.org/dbus/dbus/-/archive/dbus-{self.version}/dbus-dbus-{self.version}.tar.bz2")

    def build(self):
        env = {
            "NOCONFIGURE": "1",
        }
        args = ["--disable-static"]
        with tools.environment_append(env):
            autotools = AutoToolsBuildEnvironment(self)
            self.run("sh autogen.sh", cwd=f"dbus-dbus-{self.version}")
            autotools.configure(f"dbus-dbus-{self.version}", args)
            autotools.make()
            autotools.install()
