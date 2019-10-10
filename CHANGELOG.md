# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Metadata support: The `rgbdmux` reads per-frame metadata on the frame buffers and pushes them to a sink-pad called *meta*. Similarly, if the rgbd CAPS contains a stream called *meta*, its content is also outputted on the *meta* sink.

## Before
Prior to 0.1.2 this repository did not have a changelog.

