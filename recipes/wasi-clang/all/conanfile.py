import os

from conans import *


class WasiSdkConan(ConanFile):
    description = "WASI-enabled C/C++ toolchain"
    license = "custom"
    settings = {"os_build": ["Linux"], "arch_build": ["x86_64", "armv8"]}

    def source(self):
        tools.get(f"https://github.com/CraneStation/wasi-sdk/releases/download/wasi-sdk-{self.version.split('.')[0]}/wasi-sdk-{self.version}-linux.tar.gz")

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
