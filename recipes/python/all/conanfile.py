import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class PythonConan(ConanFile):
    name = "python"
    settings = "os", "compiler", "build_type", "arch"
    license = "MIT"
    description = "Next generation of the python high-level scripting language"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("expat/[>=2.2.7]@%s/stable" % self.user)
        self.requires("openssl/[>=1.1.1b]@%s/stable" % self.user)
        self.requires("libffi/[>=3.3]@%s/stable" % self.user)
        self.requires("zlib/[>=1.2.11]@%s/stable" % self.user)
        self.requires("bzip2/[>=1.0.8]@%s/stable" % self.user)
        self.requires("sqlite/[>=3.30.1]@%s/stable" % self.user)

    def source(self):
        tools.get("https://www.python.org/ftp/python/{0}/Python-{0}.tar.xz".format(self.version))

    def build(self):
        args = [
            "--enable-shared",
            "--with-openssl=%s" % self.deps_cpp_info["openssl"].rootpath,
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
            ldshared = "%s -pthread -shared " % os.environ["CC"]
            if self.settings.arch == "x86_64":
                ldshared += "-m64 "
            self.env_info.LDSHARED = ldshared
