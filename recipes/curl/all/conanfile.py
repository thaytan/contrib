from build import *


class CurlRecipe(Recipe):
    description = "An URL retrieval utility and library"
    license = "MIT"
    build_requires = (
        "make/[^4.3]",
        "pkgconf/[^1.7.3]",
        "zlib/[^1.2.11]",
        "openssl/[^3.0.0-alpha6]",
    )
    requires = ("ca-certificates/[^20191127]",)

    def source(self):
        self.get(f"https://curl.haxx.se/download/curl-{self.version}.tar.gz")

    def build(self):
        os.environ["CFLAGS"] += ("-ldl -lpthread",)
        self.autotools()

    def package_info(self):
        self.env_info.CURL_CA_BUNDLE = os.path.join(self.deps_cpp_info["ca-certificates"].rootpath, "etc", "ssl", "certs", "cert.pem")
