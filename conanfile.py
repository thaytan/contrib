from conans.model import Generator
from conans import ConanFile
class env(Generator):

    def __init__(self, conanfile):
        self.env = conanfile.env

    @property
    def filename(self):
        return "env.sh"

    @property
    def content(self):
        content = ""
        for var, val in self.env.items():
            if type(val) is list: 
                content += "export {0}=\"${0}\":{1}\n".format(var, ":".join(map(lambda x: "\"%s\"" % x, val)))
            else:
                content += "export {0}={1}\n".format(var, "\"%s\"" % val)

        return content


class EnvPackage(ConanFile):
    name = "env-generator"
    version = "0.1"
    url = "https://gitlab.com/aivero/public/tools/conan-env-generator"
    license = "MIT"
    description = "Generator for combined build and runtime environment file"
