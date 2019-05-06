from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import platform
import shutil

class OpensslConan(ConanFile):
    name = "openssl"
    version = "1.1.1b"
    default_user = "bincrafters"
    settings = "os", "compiler", "build_type", "arch"
    url = "https://github.com/prozum/conan-" + name
    license = "https://raw.githubusercontent.com/openssl/openssl/master/LICENSE"
    description = "TLS/SSL and crypto library"

    def source(self):
        tools.get("https://github.com/openssl/openssl/archive/OpenSSL_%s.tar.gz" % self.version.replace(".", "_"))

    def build(self):
        arch_mapper = {
            "x86_64": "x86_64",
            "armv8": "ia64"
        }
        compiler = arch_mapper[str(self.settings.arch)]
        args = ["linux-" + compiler]
        with tools.chdir(os.path.join(self.source_folder, "openssl-OpenSSL_" + self.version.replace(".", "_"))):
            shutil.copy("Configure", "configure")
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(args=args)
            autotools.make()
            autotools.install()

    def package(self):
        if self.channel == "testing":
            self.copy("*.c", "src")
            self.copy("*.h", "src")

    def package_info(self):
        self.cpp_info.libs = ["ssl", "crypto"]
        self.env_info.PKG_CONFIG_PATH.append(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for file in os.listdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            setattr(self.env_info, "PKG_CONFIG_%s_PREFIX" % file[:-3].replace(".", "_").replace("-", "_").upper(), self.package_folder)
        self.env_info.SOURCE_PATH.append(os.path.join(self.package_folder, "src"))
        self.cpp_info.srcdirs.append("src")
