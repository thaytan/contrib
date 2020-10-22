from conans import *


class ItstoolConan(ConanFile):
    description = "XML to PO and back again"
    license = "GPL3"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"
    build_requires = ("autotools/[^1.0.0]",)
    requires = ("libxml2/[^2.9.10]",)

    def requirements(self):
        self.requires(f"python/[~{self.settings.python}]")

    def source(self):
        tools.get(f"https://github.com/itstool/itstool/archive/{self.version}.tar.gz")

    def build(self):
        env = {
            "NOCONFIGURE": "1",
        }
        with tools.environment_append(env):
            self.run("sh autogen.sh", cwd=f"itstool-{self.version}")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(f"itstool-{self.version}")
            autotools.make()
            autotools.install()
