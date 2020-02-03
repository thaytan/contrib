import os

from conans import AutoToolsBuildEnvironment, ConanFile, tools


class WasiSdkConan(ConanFile):
    name = "wasi-sdk"
    version = tools.get_env("GIT_TAG", "8.0")
    settings = "os", "compiler", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "custom"
    description = "WASI-enabled C/C++ toolchain"

    def source(self):
        tools.get("https://github.com/CraneStation/wasi-sdk/releases/download/wasi-sdk-{}/wasi-sdk-{}-linux.tar.gz".format(self.version.split(".")[0], self.version))

    def package(self):
        self.copy("*", src="wasi-sdk-" + self.version)

    def package_info(self):
        self.env_info.CC = os.path.join(self.package_folder, "bin", "clang")
        self.env_info.CXX = os.path.join(self.package_folder, "bin", "clang++")
        self.env_info.LD = os.path.join(self.package_folder, "bin", "ld.lld")
        self.env_info.AS = os.path.join(self.package_folder, "bin", "llvm-as")
        self.env_info.AR = os.path.join(self.package_folder, "bin", "llvm-ar")
        self.env_info.NM = os.path.join(self.package_folder, "bin", "nm")
        self.env_info.OBJCOPY = os.path.join(self.package_folder, "bin", "llvm-objcopy")
        self.env_info.OBJDUMP = os.path.join(self.package_folder, "bin", "llvm-objdump")
        self.env_info.RANLIB = os.path.join(self.package_folder, "bin", "llvm-ranlib")
        self.env_info.SIZE = os.path.join(self.package_folder, "bin", "llvm-size")
        self.env_info.STRINGS = os.path.join(self.package_folder, "bin", "llvm-strings")
        self.env_info.STRIP = os.path.join(self.package_folder, "bin", "llvm-strip")
        self.env_info.CFLAGS += ["--target=wasm32-wasi --sysroot=" + os.path.join(self.package_folder, "share", "wasi-sysroot")]
