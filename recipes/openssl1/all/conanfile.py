from build import *


class Openssl1Recipe(Recipe):
    description = "TLS/SSL and crypto library version 1"
    license = "BSD"
    build_requires = (
        "make/[^4.3]",
        "perl/[^5.30.0]",
    )
    requires = ("ca-certificates/[^20191127]",)

    def source(self):
        self.get(f"https://github.com/openssl/openssl/archive/OpenSSL_{self.version.replace('.', '_')}.tar.gz")

    def build(self):
        self.run("mv Configure configure", cwd=f"{self.name}-{self.version}")

        args = ["shared", "no-ssl3-method"]
        if self.settings.arch_build == "x86_64":
            args += ["linux-x86_64", "enable-ec_nistp_64_gcc_128"]
        elif self.settings.arch_build == "armv8":
            args += ["linux-aarch64", "no-afalgeng"]
        self.autotools(args)

        libs = ["crypto", "ssl"]
        for lib in libs:
            os.remove(os.path.join(self.package_folder, "lib", f"lib{lib}.a"))

    def package_info(self):
        self.env_info.SSL_CERT_DIR = os.path.join(self.deps_cpp_info["ca-certificates"].rootpath, "etc", "ssl", "certs")
