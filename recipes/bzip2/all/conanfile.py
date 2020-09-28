import os

from conans import *


class Bzip2Conan(ConanFile):
    description = "A high-quality data compression program"
    license = "custom"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "make/[^4.3]",
    )

    def source(self):
        tools.get(f"https://sourceware.org/pub/bzip2/bzip2-{self.version}.tar.gz")

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            autotools = AutoToolsBuildEnvironment(self)
            self.run(f"make -f Makefile-libbz2_so CC={tools.get_env("CC")}")
            autotools.make(target="bzip2 bzip2recover", args=[f"CC={tools.get_env("CC")}"])
            autotools.install(args=["PREFIX=" + self.package_folder])

    def package(self):
        self.copy(pattern="*libbz2.so*", dst="lib", symlinks=True, keep_path=False)
        os.symlink(
            f"libbz2.so.{self.version}", os.path.join(self.package_folder, "lib", "libbz2.so"),
        )
        with tools.chdir(os.path.join(self.package_folder, "bin")):
            for source, link in (
                ("bzdiff", "bzcmp"),
                ("bzgrep", "bzegrep"),
                ("bzgrep", "bzfgrep"),
                ("bzmore", "bzless"),
            ):
                os.remove(link)
                os.symlink(source, link)
