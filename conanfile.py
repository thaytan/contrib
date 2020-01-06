import os

from conans import ConanFile, tools


class CudaConan(ConanFile):
    name = "cuda"
    version = tools.get_env("GIT_TAG", "10.1.243")
    version_driver = "418.87.00"
    description = "NVIDIA's GPU programming toolkit"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ("cuda-10.1.pc", "cudart-10.1.pc")
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("libxml2/[>=2.9.10]@%s/stable" % self.user)

    def source(self):
        tools.download(
            "http://developer.download.nvidia.com/compute/cuda/10.1/Prod/local_installers/cuda_%s_%s_linux.run"
            % (self.version, self.version_driver),
            filename="cuda_%s_%s_linux.run" %
            (self.version, self.version_driver))

    def build(self):
        self.run(
            "sh cuda_%s_%s_linux.run --silent --override-driver-check --extract=\"%s\""
            % (self.version, self.version_driver, self.build_folder))
        tools.rmdir("cublas")
        tools.rmdir("cuba-samples")
        os.remove("cuda_%s_%s_linux.run" % (self.version, self.version_driver))
        os.remove("NVIDIA-Linux-x86_64-%s.run" % self.version_driver)

    def package(self):
        for toolkit in ("cuda-toolkit", "cuda-toolkit/nvvm"):
            self.copy("*", dst="bin", src="%s/bin" % toolkit)
            self.copy("*", dst="lib64", src="%s/lib64" % toolkit)
            self.copy("*", dst="include", src="%s/include" % toolkit)
        self.copy("*.bc", src="cuda-toolkit")
        self.copy(pattern="*.pc", dst="lib/pkgconfig")
