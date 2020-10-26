from build import *


class PerlRecipe(Recipe):
    description = "A highly capable, feature-rich programming language"
    license = "GPL"
    build_requires = ("make/[^4.3]",)
    exports = "link-m-pthread.patch"

    def source(self):
        self.get(f"https://github.com/Perl/perl5/archive/v{self.version}.tar.gz")
        self.patch("link-m-pthread.patch")

    def build(self):
        self.run("mv Configure configure", cwd=f"{self.name}-{self.version}")

        args = [
            "-des",
            "-Dusethreads",
            "-Uusenm",
            "-Duseshrplib",
            "-Duselargefiles",
            "-Dprefix=" + self.package_folder,
            "-Dldflags=''",
        ]
        self.autotools(args)

    def package_info(self):
        arch_conv = {"x86_64": "x86_64", "armv8": "aarch64"}
        platform = arch_conv[str(self.settings.arch_build)] + "-linux"
        self.env_info.PERL = "perl"
        self.env_info.PERL5LIB.append(os.path.join(self.package_folder, "lib", self.version))
        self.env_info.PERL5LIB.append(os.path.join(self.package_folder, "lib", self.version, platform + "-thread-multi"))
