import os
from glob import glob

from conans import ConanFile, tools


class GccConan(ConanFile):
    name = "gcc"
    version = tools.get_env("VERSION", "7.4.0")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom", "FDL", "GPL", "LGPL"
    description = "The GNU Compiler Collection - C and C++ frontends"
    deb_pkgs = [
        "gcc-7",
        "g++-7",
        "cpp-7",
        "linux-libc-dev",
        "libc6-dev",
        "libgcc-7-dev",
        "libstdc++-7-dev",
        "libstdc++6",
        "libubsan0",
        "libasan4",
        "libgomp1",
        "libtsan0",
        "liblsan0",
        "libatomic1",
        "libcc1-0",
        "libitm1",
        "libisl19",
        "libmpfr6",
        "libmpc3",
    ]
    arch_conv = {"x86_64": "x86_64", "armv8": "aarch64"}
    generators = "env"

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)
        self.requires("binutils/[>=2.30]@%s/stable" % self.user)

    def source(self):
        if self.settings.arch == "x86_64":
            self.deb_pkgs.extend(["libmpx2", "libquadmath0", "libcilkrts5"])
        self.run("apt update")
        for pkg in self.deb_pkgs:
            self.run("apt download %s" % pkg)

    def package(self):
        # Symlink bin dir
        with tools.chdir(self.package_folder):
            os.mkdir("bin")
            os.symlink(
                "../bin", "bin/%s-linux-gnu" % self.arch_conv[str(self.settings.arch)]
            )

        # Extract and copy
        for file in os.listdir():
            if file.endswith(".deb"):
                self.run("ar x " + file)
                tools.unzip("data.tar.xz")
        for dir in ("bin", "lib", "include"):
            self.copy("*", dst=dir, src="usr/" + dir, symlinks=True)

        # Remove hardcoded path to libc_nonshared.a
        self.run(
            "sed %s/lib/%s-linux-gnu/libc.so -i -e 's/\/usr\/lib.*libc_nonshared.a/libc_nonshared.a/'"
            % (self.package_folder, self.arch_conv[str(self.settings.arch)])
        )

    def package_info(self):
        self.env_info.CC = os.path.join(self.package_folder, "bin", "gcc-7")
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "g++-7")
        self.env_info.CPATH.append(
            os.path.join(
                self.package_folder,
                "include",
                "include/%s-linux-gnu" % self.arch_conv[str(self.settings.arch)],
            )
        )
        self.env_info.LIBRARY_PATH.append(
            os.path.join(
                self.package_folder,
                "lib",
                "lib/%s-linux-gnu" % self.arch_conv[str(self.settings.arch)],
            )
        )
