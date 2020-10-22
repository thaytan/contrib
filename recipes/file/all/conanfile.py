from conans import *


class FileConan(ConanFile):
    description = "File type identification utility"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"

    def source(self):
        tools.get(f"https://astron.com/pub/file/file-{self.version}.tar.gz")

    def build(self):
        args = [
            "--disable-shared",
            "--disable-dependency-tracking",
        ]
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"file-{self.version}", args)
        autotools.make()
        autotools.install()
