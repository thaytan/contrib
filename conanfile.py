import os

from conans import ConanFile, tools


class GccConan(ConanFile):
    name = "gcc"
    version = tools.get_env("GIT_TAG", "7.4.0")
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
        # self.run("apt update")
        for pkg in self.deb_pkgs:
            self.run("apt download %s" % pkg)

    def package(self):
        arch_dir = "%s-linux-gnu" % self.arch_conv[str(self.settings.arch)]
        # Symlink arch specific paths
        with tools.chdir(self.package_folder):
            for dir in ("bin", "lib", "include"):
                os.mkdir(dir)
                os.symlink("../%s" % dir, "%s/%s" % (dir, arch_dir))
            os.symlink("gcc-7", "bin/cc")
            os.symlink("gcc-7", "bin/gcc")
            os.symlink("g++-7", "bin/c++")
            os.symlink("g++-7", "bin/g++")

        # Extract and copy
        for file in os.listdir():
            if file.endswith(".deb"):
                self.run("ar x " + file)
                tools.unzip("data.tar.xz")
        for dir in ("bin", "lib", "include"):
            self.copy("*", dst=dir, src="usr/" + dir, symlinks=True)

        # Remove hardcoded paths from ld scripts
        for script in (
            "libpthread.so",
            "gcc/x86_64-linux-gnu/7/libgcc_s.so",
            "libc.so",
            "libm.a",
            "libm.so",
        ):
            self.run(
                "sed {0}/lib/{1}/{2} -i -e 's/\/usr\/lib\/{1}\///'".format(
                    self.package_folder, arch_dir, script
                )
            )

    def package_info(self):
        arch_dir = "%s-linux-gnu" % self.arch_conv[str(self.settings.arch)]
        self.env_info.CC = os.path.join(self.package_folder, "bin", "gcc-7")
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "g++-7")
        self.env_info.CPATH.append(
            os.path.join(self.package_folder, "include", arch_dir)
        )
        self.env_info.LIBRARY_PATH.append(
            os.path.join(self.package_folder, "lib", arch_dir)
        )
