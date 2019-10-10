import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class PythonConan(ConanFile):
    name = "python"
    version = tools.get_env("GIT_TAG", "3.7.4")
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT"
    description = "Next generation of the python high-level scripting language"
    generators = "env"

    def build_requirements(self):
        self.build_requires("gcc/[>=7.4.0]@%s/stable" % self.user)
        self.build_requires("zlib/[>=1.2.11]@%s/stable" % self.user)
        self.build_requires("expat/[>=2.2.7]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get(
            "https://www.python.org/ftp/python/{0}/Python-{0}.tar.xz".format(
                self.version
            )
        )

    def build(self):
        args = [
            "--enable-shared",
            "--with-threads",
            "--with-computed-gotos",
            "--with-lto",
            "--enable-ipv6",
            "--with-system-expat",
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
