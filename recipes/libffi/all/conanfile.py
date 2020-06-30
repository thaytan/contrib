from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibffiConan(ConanFile):
    name = "libffi"
    settings = "os", "compiler", "build_type", "arch"
    license = "MIT"
    description = "A portable, high level programming interface to various calling conventions"

    def build_requirements(self):
        self.build_requires("generators/1.0.0@%s/stable" % self.user)
        self.build_requires("autotools/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://github.com/libffi/libffi/archive/v%s.tar.gz" % self.version)

    def build(self):
        args = [
            "--quiet",
            "--disable-debug",
            "--disable-dependency-tracking",
            "--disable-docs",
            "--disable-static",
            "--enable-shared",
        ]
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("sh autogen.sh")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()
            
    def package(self):
        # TODO: remove once the libs get installed into /lib instead of /lib64 by itself.
        print(self.package_folder)
        tools.mkdir("%s/lib" % self.package_folder)
        self.run("mv %s/lib64/* %s/lib/" %(self.package_folder, self.package_folder))
        tools.rmdir("%s/lib64" % self.package_folder)
