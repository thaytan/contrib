from conans import ConanFile, tools


def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "10.1.243"
    except:
        return None

class CudaConan(ConanFile):
    name = "cuda"
    version = get_version()
    version_driver = "418.87.00"
    description = "NVIDIA's GPU programming toolkit"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    settings = "os", "compiler", "build_type", "arch"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.download("http://developer.download.nvidia.com/compute/cuda/10.1/Prod/local_installers/cuda_%s_%s_linux.run" % (self.version, self.version_driver),
                       filename="cuda_%s_%s_linux.run" % (self.version, self.version_driver))

    def build(self):
        self.run("sh cuda_%s_%s_linux.run --silent --override-driver-check --extract=\"%s\"" % (self.version, self.version_driver, self.build_folder))

    def package(self):
        for toolkit in ("cuda-toolkit", "cuda-toolkit/nvvm"):
            self.copy("*", dst="bin", src="%s/bin" % toolkit)
            self.copy("*", dst="lib64", src="%s/lib64" % toolkit)
            self.copy("*", dst="include", src="%s/include" % toolkit)
        self.copy("*.bc", src="cuda-toolkit")
