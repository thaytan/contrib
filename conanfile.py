import glob
import os
import shutil

from conans import ConanFile
from conans.model import Generator


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
                    old_prefix = l.split("=")[1][:-5]
                    break
                if "includedir=" in l:
                    old_prefix = l.split("=")[1][:-9]
                    break
        if not old_prefix:
            raise Exception("Could not find package prefix in '%s'" % pc_file)
        f.seek(0)
        return f.read().replace(old_prefix, prefix)


class env(Generator):
    def __init__(self, conanfile):
        super().__init__(conanfile)

    @property
    def filename(self):
        pass

    @property
    def content(self):
        files = {"env.sh": ""}

        # Generate pc files
        for _, cpp_info in self.deps_build_info.dependencies:
            pc_paths = [
                os.path.join(cpp_info.rootpath, "lib", "pkgconfig"),
                os.path.join(cpp_info.rootpath, "share", "pkgconfig"),
               ]
            for pc_path in pc_paths:
                if not os.path.isdir(pc_path):
                    continue
                for pc in os.listdir(pc_path):
                    files[pc] = replace_prefix_in_pc_file(
                        os.path.join(pc_path, pc), cpp_info.rootpath
                    )

        # Generate pc files from PKG_CONFIG_SYSTEM_PATH
        if hasattr(self.conanfile, "system_pcs") and "PKG_CONFIG_SYSTEM_PATH" in os.environ:
            if isinstance(self.conanfile.system_pcs, str):
                self.conanfile.system_pcs = set([self.conanfile.system_pcs])
            system_pcs = set(self.conanfile.system_pcs)
            for pc_path in os.environ["PKG_CONFIG_SYSTEM_PATH"].split(os.pathsep):
                for pc in os.listdir(pc_path):
                    pc_name = os.path.splitext(pc)[0]
                    if not pc_name in self.conanfile.system_pcs:
                        continue
                    system_pcs.remove(pc_name)
                    with open(os.path.join(pc_path, pc), "r") as pc_file:
                        files[pc] = pc_file.read()
            if len(system_pcs):
                raise Exception(
                    "'%s' not available in system pkg-config directories"
                    % ", ".join(system_pcs)
                )

        # Set environment from env_info
        for var, val in self.conanfile.env.items():
            if isinstance(val, str):
                val = [val]
            files["env.sh"] += 'export {0}={1}:"${0}"\n'.format(
                var, os.pathsep.join('"%s"' % p for p in val)
            )

        return files


class tools(Generator):
    def __init__(self, conanfile):
        super().__init__(conanfile)
        self.env = conanfile.env

    @property
    def filename(self):
        pass

    @property
    def content(self):
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)

        # Generate wrapper bins
        for var, val in self.env.items():
            if isinstance(val, str):
                val = [val]
            env_vars += 'export {0}={1}:"${0}"\n'.format(
                var, os.pathsep.join('"%s"' % p for p in val)
            )

        # Find rootpath
        # 'dependencies' is not indexable
        for _, cpp_info in self.deps_build_info.dependencies:
            rootpath = cpp_info.rootpath
            break

        # Generate executable wrappers
        bin_path = os.path.join(rootpath, "bin")
        if not os.path.isdir(bin_path):
            return ""
        for exe_name in os.listdir(bin_path):
            exe_path = os.path.join(bin_path, exe_name)
            exe_out_path = os.path.join(self.output_path, exe_name)
            with open(exe_out_path, "w") as exe:
                exe.write("#!/usr/bin/env sh\n")
                exe.write(env_vars)
                exe.write('exec %s "$@"' % exe_path)
            os.chmod(exe_out_path, 0o775)

        return {}


class EnvPackage(ConanFile):
    name = "env-generator"
    version = "1.0.0"
    url = "https://gitlab.com/aivero/public/conan-env-generator"
    license = "MIT"
    description = "Generate environment file for build and runtime"
