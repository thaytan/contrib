from conans.model import Generator
from conans import ConanFile
from os import path, pathsep, listdir, environ
from shutil import copy


def replace_prefix_in_pc_file(pc_file, prefix):
    with open(pc_file) as f:
        # Get old prefix
        for l in f:
            if "prefix=" in l:
                old_prefix = l.split("=")[1][:-1]
                break

        f.seek(0)
        content=f.read().replace(old_prefix, prefix)
    with open(pc_file, "w") as f:
        f.write(content)


class env(Generator):
    def __init__(self, conanfile):
        super().__init__(conanfile)
        self.env = conanfile.env

    @property
    def filename(self):
        return "env.sh"

    @property
    def content(self):
        pc_output_path = self.output_path
        bin_paths = []
        lib_paths = []
        for _, cpp_info in self.deps_build_info.dependencies:
            lib_path = path.join(cpp_info.rootpath, "lib")
            if path.exists(lib_path):
                lib_paths.append(lib_path)
            bin_path = path.join(cpp_info.rootpath, "bin")
            if path.exists(bin_path):
                bin_paths.append(bin_path)
            pc_lib_path = path.join(cpp_info.rootpath, "lib", "pkgconfig")
            pc_share_path = path.join(cpp_info.rootpath, "share", "pkgconfig")
            if path.exists(pc_lib_path):
                for pc in listdir(pc_lib_path):
                    copy(path.join(pc_lib_path, pc), pc_output_path)
                    replace_prefix_in_pc_file(path.join(pc_output_path, pc), cpp_info.rootpath)
            if path.exists(pc_share_path):
                for pc in listdir(pc_share_path):
                    copy(path.join(pc_share_path, pc), pc_output_path)
                    replace_prefix_in_pc_file(path.join(pc_output_path, pc), cpp_info.rootpath)

        environ.update({
            "PKG_CONFIG_PATH": pc_output_path,
            "LD_LIBRARY_PATH": pathsep.join(lib_paths),
            "CFLAGS": "-fdebug-prefix-map=%s=." % self.conanfile.source_folder,
            "CXXFLAGS": "-fdebug-prefix-map=%s=." % self.conanfile.source_folder,
        })
        environ["PATH"] += pathsep + pathsep.join(bin_paths)

        content = "export PKG_CONFIG_PATH=\"$PKG_CONFIG_PATH\":\"%s\"\n" % pc_output_path
        for var, val in self.env.items():
            if type(val) is list:
                content += "export {0}=\"${0}\":{1}\n".format(var, pathsep.join(map(lambda x: "\"%s\"" % x, val)))
            else:
                content += "export {0}={1}\n".format(var, "\"%s\"" % val)

        return content


class EnvPackage(ConanFile):
    name = "env-generator"
    version = "0.1"
    url = "https://gitlab.com/aivero/public/tools/conan-env-generator"
    license = "MIT"
    description = "Generator for combined build and runtime environment file"
