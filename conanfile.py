from conans import ConanFile, tools

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "1.38.0"
    except:
        return None

class RustConan(ConanFile):
    name = "rust"
    version = get_version()
    settings = "os", "compiler", "build_type", "arch"
    url = "https://gitlab.com/aivero/public/conan/conan-" + name
    license = "MIT", "Apache"
    description = "Systems programming language focused on safety, speed and concurrency"
    generators = "env"

    def build_requirements(self):
        self.build_requires("cmake/[>=3.15.3]@%s/stable" % self.user)
        self.build_requires("python/[>=3.7.4]@%s/stable" % self.user)
        self.build_requires("libffi/[>=3.3-rc0]@%s/stable" % self.user)

    def requirements(self):
        self.requires("env-generator/[>=1.0.0]@%s/stable" % self.user)

    def source(self):
        tools.get("https://static.rust-lang.org/dist/rustc-%s-src.tar.gz" % self.version)

    def build(self):
        env = {
            "DESTDIR": self.package_folder
        }
        with tools.chdir("rustc-%s-src" % self.version), tools.environment_append(env):
            self.run("python ./x.py install")
