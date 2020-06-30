import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class GdbConan(ConanFile):
    description = "The GNU Debugger"
    license = "GPL3"
    settings = {"os": ["Linux"], "arch": ["x86_64", "armv8"]}

    def build_requirements(self):
        self.build_requires("generators/1.0.0")
        self.build_requires("gcc/[^7.4.0]")
        self.build_requires("texinfo/[^6.6]")

    def requirements(self):
        self.requires("python/[^3.7.4]")
        self.requires("ncurses/[^6.1]")
        self.requires("readline/[^8.0]")

    def source(self):
        tools.get("https://ftp.gnu.org/gnu/gdb/gdb-%s.tar.gz" % self.version)

    def build(self):
        args = ["--enable-tui=yes", "--with-system-readline"]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "share", "gdb", "python"))
