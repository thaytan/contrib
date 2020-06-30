import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class Bzip2Conan(ConanFile):
    description = "A high-quality data compression program"
    license = "custom"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("gcc/[^7.4.0]")

    def source(self):
        tools.get("https://sourceware.org/pub/bzip2/bzip2-%s.tar.gz" % self.version)

    def build(self):
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            self.run("make -f Makefile-libbz2_so CC=%s" % tools.get_env("CC"))
            autotools.make(target="bzip2 bzip2recover", args=["CC=%s" % tools.get_env("CC")])
            autotools.install(args=["PREFIX=" + self.package_folder])

    def package(self):
        self.copy(pattern="*libbz2.so*", dst="lib", symlinks=True, keep_path=False)
        os.symlink(
            "libbz2.so.%s" % self.version, os.path.join(self.package_folder, "lib", "libbz2.so"),
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
