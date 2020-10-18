from conans import *


class SharedMimeInfoConan(ConanFile):
    description = "Freedesktop.org Shared MIME Info"
    license = "GPL2"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "autotools/[^1.0.0]",
        "itstool/[^2.0.6]",
        "xz/[^5.2.4]",
    )
    requires = (
        "glib/[^2.62.0]",
        "libxml2/[^2.9.9]",
    )

    def source(self):
        tools.get(f"https://github.com/freedesktop/xdg-shared-mime-info/archive/{self.version}.tar.gz")

    def build(self):
        args = ["--disable-update-mimedb"]
        with tools.chdir(f"{self.name}-${self.version}"):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
