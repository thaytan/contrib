from build import *

CONFIG_MAK = """
CFLAGS={}
LDFLAGS=-ldl
"""


class GitRecipe(Recipe):
    description = "The fast distributed version control system"
    license = "GPL2"
    build_requires = (
        "cc/[^1.0.0]",
        "make/[^4.3]",
        "gettext/[^0.21]",
    )
    requires = (
        "curl/[^7.73.0]",
        "expat/[^2.2.7]",
        "libssl/[^1.0.0]",
    )

    def source(self):
        self.get(f"https://www.kernel.org/pub/software/scm/git/git-{self.version}.tar.xz")

    def build(self):
        with open(os.path.join(self.src, "config.mak"), "w") as cfg:
            cfg.write(CONFIG_MAK.format(f"-I{self.source_folder} {os.environ['CFLAGS']}"))
        args = [
            f"prefix={self.package_folder}",
        ]
        self.autotools(args)

    def package_info(self):
        self.env_info.GIT_SSL_CAINFO = os.path.join(self.deps_cpp_info["ca-certificates"].rootpath, "etc", "ssl", "certs", "cert.pem")
