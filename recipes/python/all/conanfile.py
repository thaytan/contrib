import os

from conans import *


class PythonConan(ConanFile):
    name = "python"
    description = "Next generation of the python high-level scripting language"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}
    build_requires = ("cc/[^1.0.0]",)
    requires = (
        "base/[^1.0.0]",
        "expat/[^2.2.7]",
        "openssl/[^1.1.1b]",
        "libffi/[^3.3]",
        "zlib/[^1.2.11]",
        "bzip2/[^1.0.8]",
        "sqlite/[^3.30.1]",
    )

    def source(self):
        tools.get(f"https://www.python.org/ftp/python/{self.version}/Python-{self.version}.tar.xz")

    def build(self):
        args = [
            "--enable-shared",
            "--with-openssl=" + self.deps_cpp_info["openssl"].rootpath,
            "--with-computed-gotos",
            "--enable-optimizations",
            "--with-lto",
            "--enable-ipv6",
            "--with-system-expat",
            "--with-system-ffi",
            "--enable-loadable-sqlite-extensions",
            "--without-ensurepip",
        ]
        with tools.chdir("Python-" + self.version):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
        os.symlink("python3.7", os.path.join(self.package_folder, "bin", "python"))

    def package_info(self):
        self.env_info.PYTHON = os.path.join(self.package_folder, "bin", "python")
        self.env_info.PYTHONHOME = self.package_folder
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.7"))
        if "CC" in os.environ:
            ldshared = os.environ["CC"] + " -pthread -shared "
            if self.settings.arch_build == "x86_64":
                ldshared += "-m64 "
            self.env_info.LDSHARED = ldshared
