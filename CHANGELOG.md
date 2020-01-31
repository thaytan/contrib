# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


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
