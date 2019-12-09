# Environment generator
A Conan generator that creates an environment file and handles the pkgconfig files of the Conan dependencies.

That involves:
- Fixing hardcoded paths in the dependencies pkgconfig files
- Copying the fixed pkgconfig files to the build directory
- Generate the `env.sh` environment file with environment variables needed for build and runtime
