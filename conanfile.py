import glob
import os
import shutil

from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.model import Generator


def replace_prefix_in_pc_file(pc_file, prefix):
    with open(pc_file) as f:
        old_prefix = ""
        # Get old prefix
        for l in f:
            if "prefix=" in l:
                old_prefix = l.split("=")[1][:-1]
                break
        f.seek(0)
        if not old_prefix:
            for l in f:
                if "libdir=" in l:
                    old_prefix = l.split("=")[1][:-5]
                    break
                if "includedir=" in l:
                    old_prefix = l.split("=")[1][:-9]
                    break
        if not old_prefix:
            raise Exception("Could not find package prefix in '%s'" % pc_file)
        f.seek(0)
        return f.read().replace(old_prefix, prefix)


class pkgconf(Generator):
    def __init__(self, conanfile):
        super().__init__(conanfile)

    @property
    def filename(self):
        pass

    @property
    def content(self):
        files = {}

        # Generate pc files
        for _, cpp_info in self.deps_build_info.dependencies:
            pc_paths = [
                os.path.join(cpp_info.rootpath, "lib", "pkgconfig"),
                os.path.join(cpp_info.rootpath, "share", "pkgconfig"),
            ]
            for pc_path in pc_paths:
                if not os.path.isdir(pc_path):
                    continue
                for pc in os.listdir(pc_path):
                    files[pc] = replace_prefix_in_pc_file(os.path.join(pc_path, pc), cpp_info.rootpath)

        # Generate pc files from PKG_CONFIG_SYSTEM_PATH
        if hasattr(self.conanfile, "system_pcs") and "PKG_CONFIG_SYSTEM_PATH" in os.environ:
            if isinstance(self.conanfile.system_pcs, str):
                self.conanfile.system_pcs = set([self.conanfile.system_pcs])
            system_pcs = set(self.conanfile.system_pcs)
            for pc_path in os.environ["PKG_CONFIG_SYSTEM_PATH"].split(os.pathsep):
                for pc in os.listdir(pc_path):
                    pc_name = os.path.splitext(pc)[0]
                    if not pc_name in self.conanfile.system_pcs:
                        continue
                    system_pcs.remove(pc_name)
                    with open(os.path.join(pc_path, pc), "r") as pc_file:
                        files[pc] = pc_file.read()
            if len(system_pcs):
                raise Exception("'%s' not available in system pkg-config directories" % ", ".join(system_pcs))

        return files


class PkgconfConan(ConanFile):
    name = "pkgconf"
    version = tools.get_env("GIT_TAG", "1.6.3")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    description = "Package compiler and linker metadata toolkit"

    def build_requirements(self):
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("autoconf/[>=2.69]@%s/stable" % self.user)
        self.build_requires("automake/[>=1.16.1]@%s/stable" % self.user)
        self.build_requires("libtool/[>=2.4.6]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/pkgconf/pkgconf/archive/pkgconf-%s.tar.gz" % self.version)

    def build(self):
        args = ["--disable-static"]
        with tools.chdir("pkgconf-pkgconf-%s" % self.version):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
        os.symlink("pkgconf", os.path.join(self.package_folder, "bin", "pkg-config"))

    def package_info(self):
        self.env_info.PKG_CONFIG = os.path.join(self.package_folder, "bin", "pkgconf")
        self.env_info.ACLOCAL_PATH.append(os.path.join(self.package_folder, "share", "aclocal"))
        # Support system pkgconfig files
        if self.settings.os == "Linux":
            self.env_info.PKG_CONFIG_SYSTEM_PATH.append("/usr/share/pkgconfig")
            if self.settings.arch == "x86_64":
                self.env_info.PKG_CONFIG_SYSTEM_PATH.append("/usr/lib/x86_64-linux-gnu/pkgconfig")
            if self.settings.arch == "armv8":
                self.env_info.PKG_CONFIG_SYSTEM_PATH.append("/usr/lib/aarch64-linux-gnu/pkgconfig")
