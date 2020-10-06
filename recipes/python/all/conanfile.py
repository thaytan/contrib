import os

from conans import *


class PythonConan(ConanFile):
    description = "Next generation of the python high-level scripting language"
    license = "MIT"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build"
    build_requires = (
        "bootstrap-llvm/[^10.0.1]",
        "make/[^4.3]",
        "expat/[^2.2.7]",
        "openssl/[^3.0.0-alpha6]",
        "libffi/[^3.3]",
        "zlib/[^1.2.11]",
        "bzip2/[^1.0.8]",
        "sqlite/[^3.30.1]",
        "readline/[^8.0]",
    )

    def source(self):
        tools.get(f"https://www.python.org/ftp/python/{self.version}/Python-{self.version}.tar.xz")

    def build(self):
        # Python build scripts handles LTO
        env = {
            "CFLAGS": os.environ["CFLAGS"].replace("-flto=thin", ""),
        }
        args = [
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
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(f"Python-{self.version}", args, vars=env)
        autotools.make()
        autotools.install()
        os.symlink("python3.8", os.path.join(self.package_folder, "bin", "python"))

    def package_info(self):
        self.env_info.PYTHON = os.path.join(self.package_folder, "bin", "python")
        self.env_info.PYTHONHOME = self.package_folder
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.8"))
        if "CC" in os.environ:
            ldshared = os.environ["CC"] + " -pthread -shared "
            if self.settings.arch_build == "x86_64":
                ldshared += "-m64 "
            self.env_info.LDSHARED = ldshared
