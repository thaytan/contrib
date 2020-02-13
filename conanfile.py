from conans import ConanFile


class EnvPackage(ConanFile):
    name = "env-generator"
    version = "1.0.0"
    url = "https://gitlab.com/aivero/public/conan-" + name
    license = "MIT"
    description = "Generate environment file for build and runtime"

    def requirements(self):
        self.requires("generators/1.0.0@%s/stable" % self.user)
