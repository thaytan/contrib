from conans import *


class LibxsltConan(ConanFile):
    description = "XML stylesheet transformation library"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = ("autotools/[^1.0.0]",)
    requires = ("libxml2/[^2.9.10]",)

    def source(self):
        tools.get(f"https://gitlab.gnome.org/GNOME/libxslt/-/archive/v{self.version}/libxslt-v{self.version}.tar.gz")

    def build(self):
        env = {
            "NOCONFIGURE": "1",
        }
        args = [
            "--disable-static",
            "--without-python",
        ]
        with tools.environment_append(env):
            autotools = AutoToolsBuildEnvironment(self)
            self.run("sh autogen.sh", cwd=f"libxslt-v{self.version}")
            autotools.configure(f"libxslt-v{self.version}", args)
            autotools.make()
            autotools.install()
