from build import *


class BionicRecipe(Recipe):
    ndk_version = "21d"
    description = "Bionic C Library"
    license = "Apache-2.0"
    settings = "build_type", "compiler", "arch", "os", "libc"
    options = {}
    default_options = {}

    def source(self):
        tools.get(f"https://dl.google.com/android/repository/android-ndk-r{self.ndk_version}-linux-x86_64.zip")

    def build(self):
        pass

    def package(self):
        arch = {"x86_64": "x86_64", "armv8": "arm64"}[str(self.settings.arch)]
        lib = os.path.join(f"android-ndk-r{self.ndk_version}", "platforms", f"android-{self.settings.os.api_level}", f"arch-{arch}", "usr", "lib")
        inc = os.path.join(f"android-ndk-r{self.ndk_version}", "sysroot", "usr", "include")
        self.copy(pattern="*", src=lib, dst="lib", keep_path=False)
        self.copy(pattern="*", src=inc, dst="include", keep_path=False)

    def package_info(self):
        self.env_info.LIBC_LIBRARY_PATH = os.path.join(self.package_folder, "lib")
        self.env_info.LIBC_INCLUDE_PATH = os.path.join(self.package_folder, "include")
