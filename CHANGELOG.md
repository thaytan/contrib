# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.5] - 2020-07-01
### Changed
- Add gstreamer conan setting and depend on it for gst deps
## [0.1.1] - 2019-09-23
### Changed
- The colorizer now sets all pixels have `value >= farcut || value < nearcut`
to 0. This solves an issue that arose when the near-cut or far-cut on the
colorizer does not align with that of the `dddqdec`.

## [0.1.0] - Prior to 2019-09-23
Before [0.1.1] this project did not have a changelog.
