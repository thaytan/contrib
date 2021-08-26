project('contrib',
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

include = []
subdir('gst-depth-meta')
