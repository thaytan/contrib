from conans import *


class LibffiBootstrapConan(ConanFile):
    name = "libffi-bootstrap"
    description = "A portable, high level programming interface to various calling conventions"
    license = "MIT"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self)    build_requires = ("autotools/[^1.0.0]",):
        tools.get(f"https://github.com/libffi/libffi/archive/v{self.version}.tar.gz")

    def build(self):
        args = [
            "--quiet",
            "--disable-debug",
            "--disable-dependency-tracking",
            "--disable-docs",
            "--disable-static",
            "--enable-shared",
        ]
        with tools.chdir(f"libffi-{self.version}"):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package(self):
        # TODO: remove once the libs get ins.
        print(self.package_folder)
        tools.mkdir(f"{self.package_folder}/lib")
        self.run(f"mv {self.package_folder}/lib64/* {self.package_folder}/lib/")
        tools.rmdir(f"{self.package_folder}/lib64")
