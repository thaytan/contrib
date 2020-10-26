from build import *


class CaCertificatesRecipe(Recipe):
    description = "Common CA certificates PEM files from Mozilla"
    license = "MPL-2.0"
    settings = "build_type", "compiler", "arch_build", "os_build", "libc_build", "python"

    build_requires = (
        "openssl/[^3.0.0-alpha6]",
        "make/[^4.3]",
    )

    def build_requirements(self):
        self.build_requires(f"python/[~{self.settings.python}]")

    def source(self):
        self.get(f"https://gitlab.alpinelinux.org/alpine/ca-certificates/-/archive/{self.version}/ca-certificates-{self.version}.tar.bz2")

    def build(self):
        os.environ["DESTDIR"] = self.package_folder
        os.environ["CFLAGS"] += f" -ldl -lpthread -I{self.deps_cpp_info['openssl'].rootpath}/include"
        self.make(install=False)

        # Combine certs to ca-certificates.crt
        with tools.chdir(f"ca-certificates-{self.version}"):
            # NetLock Arany contains invalid utf-8 characters, which is not supported in Python 3.6
            self.run("mv NetLock_Arany_*.crt NetLock_Arany.crt")
            with open("ca-certificates.crt", "w") as ca_cert:
                for cert in glob.glob("*.crt"):
                    ca_cert.write(pathlib.Path(cert).read_text())
        os.symlink("ca-certificates.crt", "cert.pem")

    def package(self):
        self.copy("*.crt", dst="share/ca-certificates", keep_path=False)
        self.copy("*ca-certificates.crt", dst="etc/ssl/certs")
        self.copy("*cert.pem", dst="etc/ssl/certs", symlinks=True)
