import glob
import os
import shutil

from conans import ConanFile
from conans.model import Generator


class env(Generator):
    def __init__(self, conanfile):
        super().__init__(conanfile)

    @property
    def filename(self):
        pass

    @property
    def content(self):
        # Set environment from env_info
        files = {"env.sh": 'export PKG_CONFIG_PATH="{}"\n'.format(self.output_path)}
        for var, val in self.conanfile.env.items():
            if isinstance(val, str):
                val = [val]
            if len(val) > 1:
                files["env.sh"] += 'export {0}={1}"\$\{${0}:+:${0}\}"\n'.format(var, os.pathsep.join('"%s"' % p for p in val))
            else:
                files["env.sh"] += 'export {0}={1}\n'.format(var, '"%s"' % val[0])

        return files


class tools(Generator):
    def __init__(self, conanfile):
        super().__init__(conanfile)

    @property
    def filename(self):
        pass

    @property
    def content(self):
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)

        # Generate wrapper bins
        env_vars = ""
        for var, val in self.conanfile.env.items():
            if isinstance(val, str):
                val = [val]
            if len(val) > 1:
                env_vars += 'export {0}={1}:"${0}"\n'.format(var, os.pathsep.join('"%s"' % p for p in val))
            else:
                env_vars += 'export {0}={1}\n'.format(var, '"%s"' % val[0])

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


class GeneratorsPackage(ConanFile):
    name = "generators"
    version = "1.0.0"
    url = "https://gitlab.com/aivero/public/conan-env-generator"
    license = "MIT"
    description = "Conan generators"
