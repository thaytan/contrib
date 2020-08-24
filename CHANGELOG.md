# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.3] - 2020-08-24

### Changed

- Bump version of dep k4a-rs to 0.4.7
- Bump version of dep gstreamer-depth-meta to 1.3.0


## [1.3.2] - 2020-08-03

### Changed

- Bump version of dep k4a-rs to 0.4.6

## [1.3.1] - 2020-07-31

### Changed

- Bump version of dep k4a-rs to 0.4.5

## [1.3.0] - 2020-07-03

### Added

- Pipeline test runs on gst-validation-toolkit.

### Changed

- Make enums public

## [1.2.1] - 2020-07-01

### Changed

- Add gstreamer conan setting


## [1.2.0] - 2020-06-25

### Added

- Armv8 support

## [1.1.2] - 2020-05-26

### Changed

- Bump dependency k4a-rs to 0.4.2, which is also at a new location, the `public` subgroup.
- Bump dependency gst-depth-meta-rs to 1.2.0

## [1.1.1] - 2020-04-29

### Fixed

- Panic caused by double-registration of the GstTimestampMode enum.

## [1.1.0] - 2020-04-02
### Added
- Accept "~/path/to/file", i.e. tilde as $HOME, while setting `recording-location`.
### Changed
- Update dependencies
  - `glib` to 0.9
  - `gst` to 0.15

## [1.0.0] - 2020-03-26

### Changed

- Use implementation of standard `RgbdTimestamps` trait instead of custom timestamping. This includes renaming of variants `k4a_common` to `camera_common` and `k4a_individual` to `camera_individual`.

## [0.5.0] - 2020-03-04

### Added

- Implemented attaching of camera meta containing intrinsics, extrinsics and depth scale. This functionality can be enabled by `attach-camera-meta` property.

### Modified
- Use of standard function for work with `video/rgbd` CAPS from `gst_depth_meta::rgbd` module, instead of custom-local implementation.

### Fixed
- Setting of `framerate` and `timestamp-mode` properties.

## [0.4.0] - 2020-02-18

### Added

- Implemented rectification of depth, which can be enabled by `rectify-depth` property.

## [0.3.0] - 2020-02-18

### Changed

- Implemented `GEnum` properties for all enum-like int properties on the `k4asrc`.

## [0.2.0] - 2020-02-17

### Added

- Expand timestamping capabilities, i.e. `timestamp-mode` property that can take the following forms: `ignore`, `main`, `all`, `k4a_common` and `k4a_individual`
- Support for MJPG

### Modified

- Fix streaming from Playback.

## [0.1.0] - 2020-01-24

### Added

- First version of `k4asrc`
