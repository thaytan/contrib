import os

from conans import ConanFile, tools

driver_map = {"10.1.243": "418.87.00"}


class CudaConan(ConanFile):
    name = "cuda"
    version = tools.get_env("GIT_TAG", "10.1.243")
    description = "NVIDIA's GPU programming toolkit"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ("cuda-10.1.pc", "cudart-10.1.pc")
    generators = "env"

    def build_requirements(self):
        self.build_requires("env-generator/1.0.0@%s/stable" % self.user)
        self.build_requires("gcc/7.4.0@%s/stable" % self.user)
        self.build_requires("libxml2/[>=2.9.10]@%s/stable" % self.user)

    def source(self):
        tools.download("http://developer.download.nvidia.com/compute/cuda/10.1/Prod/local_installers/cuda_%s_%s_linux.run" % (self.version, driver_map[self.version]),
                       filename="cuda_%s_linux.run" % self.version)

    def build(self):
        self.run("sh cuda_%s_linux.run --silent --override-driver-check --extract=\"%s\"" % (self.version, self.build_folder))
        os.remove("cuda_%s_linux.run" % self.version)
        self.run("sh NVIDIA-Linux-x86_64-%s.run --extract-only" % driver_map[self.version])
        os.remove("NVIDIA-Linux-x86_64-%s.run" % driver_map[self.version])
        tools.rmdir("cublas")
        tools.rmdir("cuba-samples")

    def package(self):
        for toolkit in ("cuda-toolkit", "cuda-toolkit/nvvm"):
            self.copy("*", dst="bin", src="%s/bin" % toolkit)
            self.copy("*", dst="lib", src="%s/lib64" % toolkit)
            self.copy("*", dst="include", src="%s/include" % toolkit)
        self.copy("*.bc", src="cuda-toolkit")
        self.copy("*libcuda.so*", dst="lib", keep_path=False, symlinks=True)
        self.copy("*libnvcuvid.so*", dst="lib", keep_path=False, symlinks=True)
        with tools.chdir(os.path.join(self.package_folder, "lib")):
            os.symlink("libnvcuvid.so.418.87.00", "libnvcuvid.so.1")
            os.symlink("libnvcuvid.so.1", "libnvcuvid.so")
        self.copy(pattern="*.pc", dst="lib/pkgconfig")
