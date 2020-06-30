import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class GdbConan(ConanFile):
    name = "gdb"
    description = "The GNU Debugger"
    license = "GPL3"
    settings = "os", "arch", "compiler"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("texinfo/[>=6.6]@%s/stable" % self.user)

    def requirements(self):
        self.requires("python/[>=3.7.4]@%s/stable" % self.user)
        self.requires("ncurses/[>=6.1]@%s/stable" % self.user)
        self.requires("readline/[>=8.0]@%s/stable" % self.user)

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
