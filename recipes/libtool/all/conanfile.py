import os

from conans import *


class LibtoolConan(ConanFile):
    name = "libtool"
    description = "A generic library support script"
    license = "GPL"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    exports = "libtool-prefix-fix.patch"
    build_requires = (
        "cc/[^1.0.0]",
        "autoconf/[^2.69]",
        "automake/[^1.16.1]",
        "help2man/[^1.47.11]",
        "texinfo/[^6.6]",
    )

    def source(self):
        git = tools.Git(folder=f"{self.name}-{self.version}")
        git.clone("https://git.savannah.gnu.org/git/libtool.git", "v" + self.version)
        git = tools.Git(folder="gnulib")
        git.clone("https://git.savannah.gnu.org/git/gnulib.git")
        git = tools.Git(folder="gnulib-bootstrap")
        git.clone("https://github.com/gnulib-modules/bootstrap.git")
        tools.patch(
            patch_file="libtool-prefix-fix.patch", base_path=f"{self.name}-{self.version}",
        )

    def build(self):
        with tools.chdir(f"{self.name}-{self.version}"):
            self.run("git submodule init")
            self.run('git config --local submodule.gnulib.url "%s/gnulib"' % self.source_folder)
            self.run('git config --local submodule.gl-mod/bootstrap.url "%s/gnulib-bootstrap"' % self.source_folder)
            self.run("git submodule update")
            self.run("./bootstrap")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure()
            autotools.make()
            autotools.install()

    def package_info(self):
        self.env_info.LIBTOOL_PREFIX = self.package_folder
        self.env_info.LIBTOOL = os.path.join(self.package_folder, "bin", "libtool")
        self.env_info.LIBTOOLIZE = os.path.join(self.package_folder, "bin", "libtoolize")
        self.env_info.ACLOCAL_PATH.append(os.path.join(self.package_folder, "share", "aclocal"))
