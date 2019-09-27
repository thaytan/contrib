from conans.model import Generator
from conans import ConanFile
from os import path, pathsep, listdir, environ, makedirs
from shutil import copy


def replace_prefix_in_pc_file(pc_file, prefix):
    with open(pc_file) as f:
        old_prefix = ""
        # Get old prefix
        for l in f:
            if "prefix=" in l:
                old_prefix = l.split("=")[1][:-1]
                break
        f.seek(0)
        if not old_prefix:
            for l in f:
                if "libdir=" in l:
                    old_prefix = l.split("=")[1][:-1]
                    break

        f.seek(0)
        content=f.read().replace(old_prefix, prefix)
    with open(pc_file, "w") as f:
        f.write(content)

def env_prepend(var, val):
    environ[var] = val + (pathsep + environ[var] if var in environ else "")

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
        if not path.exists(pc_output_path):
            makedirs(pc_output_path)

        # Find bin, lib and pkgconfig paths
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

        # Update Conan environment
        env_prepend("PATH", pathsep.join(bin_paths))
        env_prepend("PKG_CONFIG_PATH", pc_output_path)
        env_prepend("LD_LIBRARY_PATH", pathsep.join(lib_paths))
        if hasattr(self.conanfile, "source_folder"):
            env_prepend("CFLAGS", " -fdebug-prefix-map=%s=. " % self.conanfile.source_folder)
            env_prepend("CXXFLAGS", " -fdebug-prefix-map=%s=. " % self.conanfile.source_folder)

        # Generate env.sh
        content = "export PATH=%s:\"$PATH\"\n" % pathsep.join(map(lambda path: "\"%s\"" % path, bin_paths))
        content += "export PKG_CONFIG_PATH=\"%s\":\"$PKG_CONFIG_PATH\"\n" % pc_output_path
        content += "export LD_LIBRARY_PATH=%s:\"$LD_LIBRARY_PATH\"\n" % pathsep.join(map(lambda path: "\"%s\"" % path, lib_paths))

        for var, val in self.env.items():
            if type(val) is list:
                content += "export {0}={1}:\"${0}\"\n".format(var, pathsep.join(map(lambda path: "\"%s\"" % path, val)))
            else:
                content += "export {0}={1}\n".format(var, "\"%s\"" % val)

        return content


class EnvPackage(ConanFile):
    name = "env-generator"
    version = "1.0.0"
    url = "https://gitlab.com/aivero/public/tools/conan-env-generator"
    license = "MIT"
    description = "Generator for combined build and runtime environment file"
