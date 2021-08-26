project('aivero',
        'rust',
        'c',
        version: '0.13.0',
        meson_version : '>= 0.56')

if get_option('debug')
  target = 'debug'
else
  target = 'release'
endif

cargo = find_program('cargo', version:'>=1.40')
cargo_wrapper = find_program('cargo_wrapper.py')
cargo_c = find_program('cargo-cbuild', required: false)
rustc = find_program('rustc', version:'>=1.52')

if not cargo_c.found()
  error('cargo-c missing, install it with: \'cargo install cargo-c\'')
endif

system = build_machine.system()
if system == 'windows'
  ext_dynamic = 'dll'
  ext_static = 'lib'
elif system == 'darwin'
  ext_dynamic = 'dylib'
  ext_static = 'a'
else
  ext_dynamic = 'so'
  ext_static = 'a'
endif

plugins_rep = {
  'gst-depth-meta': 'libdepth-meta',
}

include = ['./gst-depth-meta']
extra_env = {}


cc = meson.get_compiler('c')


output = []

extensions = []

# Add the plugin file as output
if get_option('default_library') == 'shared' or get_option('default_library') == 'both'
  extensions += [ext_dynamic]
  foreach p, lib : plugins_rep
    output += [lib + '.' + ext_dynamic]
  endforeach
endif

if get_option('default_library') == 'static' or get_option('default_library') == 'both'
  extensions += [ext_static]
  foreach p, lib : plugins_rep
    output += [lib + '.' + ext_static]
  endforeach
endif

pc_files = []
foreach p, lib : plugins_rep
  # skip the 'lib' prefix in plugin name
  pc_files += [lib.substring(3) + '.pc']
endforeach

# Need to depends on all gstreamer-rs deps to ensure they are built
# before gstreamer-rs when building with gst-build.
# Custom targets can't depend on dependency() objects so we have to depend
# on the library variable from the subproject instead.
gst_req = '>= 1.14.0'
depends = []

deps = [
  # name, subproject name, subproject dep, library object
  ['gstreamer-1.0', 'gstreamer', 'gst_dep', 'libgst'],
  ['gstreamer-app-1.0', 'gst-plugins-base', 'app_dep', 'gstapp'],
  ['gstreamer-audio-1.0', 'gst-plugins-base', 'audio_dep', 'gstaudio'],
  ['gstreamer-base-1.0', 'gstreamer', 'gst_base_dep', 'gst_base'],
  ['gstreamer-check-1.0', 'gstreamer', 'gst_check_dep', 'gst_check'],
  ['gstreamer-net-1.0', 'gstreamer', 'gst_net_dep', 'gst_net'],
  ['gstreamer-rtp-1.0', 'gst-plugins-base', 'rtp_dep', 'gst_rtp'],
  ['gstreamer-video-1.0', 'gst-plugins-base', 'video_dep', 'gstvideo'],
  ['gst-depth-meta', 'gst-depth-meta', 'gst_depth_meta_dep', 'depth-meta'],
]

foreach d: deps
  dep = dependency(d[0], version : gst_req,
    fallback : [d[1], d[2]])
  if dep.type_name() == 'internal'
    lib = subproject(d[1]).get_variable(d[3])
    depends += lib
  endif
endforeach

include = ','.join(include)
# serialize extra_env
extra_env_list = []
foreach key, value : extra_env
  extra_env_list += key + ':' + value
endforeach
extra_env_str = ','.join(extra_env_list)

plugins_install_dir = get_option('libdir') / 'gstreamer-1.0'
pkgconfig_install_dir = get_option('libdir') / 'pkgconfig'

# Always build the target so we don't have to list all source files as input
rs_plugins = custom_target('aivero',
  build_by_default: true,
  output: output,
  console: true,
  install: true,
  install_dir: plugins_install_dir,
  build_always_stale: true,
  depends: depends,
  command: [cargo_wrapper,
    'build',
    meson.current_build_dir(),
    meson.current_source_dir(),
    meson.build_root(),
    target,
    include,
    extra_env_str,
    get_option('prefix'),
    get_option('libdir'),
    extensions])

plugins = rs_plugins.to_list()

# We don't need to pass a command as we depends on the target above
# but it is currently mandatory ( https://github.com/mesonbuild/meson/issues/8059 )
# so use python as it's guaranteed to be present on any setup
python = import('python').find_installation()
custom_target('aivero-pc-files',
  build_by_default: true,
  output: pc_files,
  console: true,
  install: true,
  install_dir: pkgconfig_install_dir,
  depends: rs_plugins,
  command: [python, '-c', '""'])

test('tests',
  cargo_wrapper,
  args: ['test',
    meson.current_build_dir(),
    meson.current_source_dir(),
    meson.build_root(),
    target,
    include,
    extra_env_str,
    get_option('prefix'),
    get_option('libdir')],
  timeout: 600)
