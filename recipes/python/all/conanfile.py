from build import *


class PythonRecipe(PythonRecipe):
    description = "Next generation of the python high-level scripting language"
    license = "MIT"
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
    )
    requires = (
        "libssl/[^1.0.0]",
        "expat/[^2.2.7]",
        "libffi/[^3.3]",
        "bzip2/[^1.0.8]",
        "sqlite/[^3.30.1]",
    )

    def source(self):
        self.get(f"https://www.python.org/ftp/python/{self.version}/Python-{self.version}.tar.xz")

    def build(self):
        # Python build scripts handles LTO
        env_replace("CFLAGS", "-flto=thin")

        args = [
            f"--with-openssl={self.deps_cpp_info['openssl'].rootpath}",
            "--with-computed-gotos",
            "--enable-optimizations",
            "--enable-ipv6",
            "--with-system-expat",
            "--with-system-ffi",
            "--enable-loadable-sqlite-extensions",
            "--without-ensurepip",
        ]
        if not self.options.shared:
            args.append("--with-lto")

        self.autotools(args)

        os.symlink(f"python{self.settings.python}", os.path.join(self.package_folder, "bin", "python"))

    def package_info(self):
        self.env_info.PYTHON = os.path.join(self.package_folder, "bin", "python")
        self.env_info.PYTHONHOME = self.package_folder
        if "CC" in os.environ:
            ldshared = os.environ["CC"] + " -pthread -shared "
            if self.settings.arch == "x86_64":
                ldshared += "-m64 "
            self.env_info.LDSHARED = ldshared
