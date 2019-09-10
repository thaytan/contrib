from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os

def get_version():
    git = tools.Git()
    try:
        tag = git.get_tag()
        return tag if tag else "2.6.4"
    except:
        return None

class FlexConan(ConanFile):
    name = "flex"
    version = get_version()
    url = "https://gitlab.com/aivero/public/conan/conan-flex"
    description = "Flex, the fast lexical analyzer generator"
    license = "BSD 2-Clause"
    settings = "os", "arch", "compiler", "build_type"
    generators = "env"

    def requirements(self):
        self.requires("env-generator/0.1@%s/%s" % (self.user, self.channel))
        self.requires("bison/3.3@%s/%s" % (self.user, self.channel), private=True)

    def source(self):
        tools.get("https://github.com/westes/flex/releases/download/v{0}/flex-{0}.tar.gz".format(self.version))

    def build(self):
        args = ["--disable-nls", "ac_cv_func_reallocarray=no"]
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir("%s-%s" % (self.name, self.version)):
            self.run("./autogen.sh")
            autotools.configure(args=args)
            autotools.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
