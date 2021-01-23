# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2020-Nov-18

### Added
- `Device::open_first_unused()`, which allows opening of first UNUSED device as per https://gitlab.com/aivero/public/gstreamer/gst-k4a/-/issues/16.

### Changed
- Fixed multi-camera support

## [0.4.7] - 2020-07-31
### Changed
- Bump dep version k4a-sys to 0.1.6 due to bindgen 0.55.0

## [0.4.6] - 2020-07-31
### Fixed
- Cast data type for vec lengths returned from bindgen bindings from u64 to usize. Necessary to support bindgen 0.54.1

## [0.4.5] - 2020-07-31
### Changed
- Bump dep version k4a-sys to 0.1.5

## [0.4.4] - 2020-06-24

### Fixed
- Data type for byte array pointer, used by `k4a_calibration_get_from_raw()`, which needs to be different for x86_64 and aarch64 builds

## [0.4.3] - 2020-06-17

### Fixed
- Error implementation of K4aError, which was causing infinite loop

## [0.4.2] - 2020-05-26

### Changed
- Added MIT license
- Bumped k4a-sys dependency to 0.1.4
- Make conan dependencies dynamic
- Move to public subgroup

## [0.4.1] - 2020-02-27

### Changed

- Made parameters contained within `IntrinsicsParameters` public.

## [0.4.0] - 2020-02-18

### Added

- `Calibration::default()` implementation.
- Allow `Transformation` to move between threads by adding `Send` and `Sync` implementations.

### Changed

- Replaced the `Transformation` member `&Calibration` with `Resolution` for depth and color as that is all we need.

## [0.3.0] - 2020-02-18

### Added

- `Calibration::extrinsics(source,target)` function, which allows the user to obtain the extrinsics between source and target.

## [0.2.0] - 2020-02-18

### Added

- `CameraCalibration` wrapper, which allows the user to inspect and use the camera calibration.
- `Intrinsics` wrapper.
- `Extrinsics` wrapper.

## [0.1.3] - 2020-01-31
### Modified
- Return `Result<Image>` from `Capture::get_X_image()` instead of just `Image` to accound for possible failure.

## [0.1.2] - 2019-12-04
### Added
- Small helper functions for work with generated enums under `utilities.rs`
### Performed
- Performed first tests with physical device and recording
- Fixed issues with passing of handles
- Fixed issues with allocating memory for CString returned by several functions

## [0.1.1] - 2019-11-13
### Added
- Add `K4aError`.
- Add linking to structs and methods in documentation.
- Add this `CHANGELOG.md`.
### Modified
- Use `VectorXYZ` to contain output from `ImuSample` accelerometer and gyroscope instead of `[f32, 3]`.
- Make use of `K4aError`.
- Make use of the Rustified struct implemented in `k4a-sys` "0.1.1".
- Format documentation.
- Update `README.md`.

## [0.1.0]
### Added
- Prior to 0.1.1 this repository did not have a changelog.
