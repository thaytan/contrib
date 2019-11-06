# gst-depth-meta-rs

This repository contains the rust bindings for `gst-depth-meta` ([this repository](https://gitlab.com/aivero/public/gstreamer/gst-depth-meta)), which is used to add MetaData onto GStreamer Buffers. Metadata currently comes in two forms:

1. BufferMeta, which allows developers to add buffers as metadata onto other buffers.
2. TagsMeta, which allows developers to tag buffers, such that their content can be identified later downstream.

## Use

`gst-depth-meta-rs` is used in Aivero's custom Rust-based GStreamer elements:

- [gst-depth-codec-rs](https://gitlab.com/aivero/streaming/gst-depth-codec-rs)
- [gst-rgbd](https://gitlab.com/aivero/public/gstreamer/gst-rgbd)
- [gst-3dq-bin](https://gitlab.com/aivero/streaming/gst-3dq-bin)
- [gst-depth-webrtc](https://gitlab.com/aivero/streaming/gst-depth-webrtc)
- [gst-realsense](https://gitlab.com/aivero/public/gstreamer/gst-realsense)

## Examples

Please see https://aivero.gitlab.io/aivero-architecture/documents/h-cross-cutting-concepts/d-rgbd-caps.html for an example of how the `gst-depth-meta` is used.