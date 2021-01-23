# gst-depth-meta-rs

This repository contains the rust bindings for `gst-depth-meta` ([this repository](https://gitlab.com/aivero/public/gstreamer/gst-depth-meta)), which is used to add MetaData onto GStreamer Buffers. Metadata currently comes in two forms:

1. BufferMeta, which allows developers to add buffers as metadata onto other buffers.
2. TagsMeta, which allows developers to tag buffers, such that their content can be identified later downstream.

To interface with both BufferMeta and TagsMeta, it is recommended to utilise the safe functions from the [`rgbd`](src/rgbd/rgbd.rs) module.

This project also contains [`rgbd_timestamps`](src/rgbd_timestamps/rgbd_timestamps.rs) module that provide standard way of timestamping `video/rgbd` buffers.

Furthermore, this project repository contains [`camera_meta`](src/camera_meta/camera_meta.rs) module that provides list of all [`intrinsics`](src/camera_meta/intrinsics.rs) and [`extrinsics`](src/camera_meta/transformation.rs) for a calibrated camera setup, alongside (de)serialisation with *Cap'n Proto*.

## Use

`gst-depth-meta-rs` is used in Aivero's custom Rust-based GStreamer elements:

- [gst-depth-codec-rs](https://gitlab.com/aivero/streaming/gst-depth-codec-rs)
- [gst-rgbd](https://gitlab.com/aivero/public/gstreamer/gst-rgbd)
- [gst-3dq-bin](https://gitlab.com/aivero/streaming/gst-3dq-bin)
- [gst-depth-webrtc](https://gitlab.com/aivero/streaming/gst-depth-webrtc)
- [gst-realsense](https://gitlab.com/aivero/public/gstreamer/gst-realsense)
- [gst-k4a](https://gitlab.com/aivero/public/gstreamer/gst-k4a)

## Examples

### Buffer structure

The following example uses JSON to outline an example buffer structure. The main buffer is tagged using the `TagsMeta` as *"depth"*. It contains two additional buffers, which are attached using the `BufferMeta`. Those buffers are *"infra1"* and *"color"*, respectively. This buffer structure is used when running the `realsensesrc` as `realsensesrc enable-depth=true enable-infra1=true enable-color=true`.

```json
{
    "TagsMeta": [ { "Title": "depth" } ],
    "BufferMeta": [
        {
            "TagsMeta": [ { "Title": "infra1" } ]
        },
        {
            "TagsMeta": [ { "Title": "color" } ]
        }
    ]
}
```

### Tag a buffer

This example creates a new buffer and gives it the title `"title"`.

```rust
// Create a new buffer
let mut buffer = gst::Buffer::new();

// Create a TagList, which holds the tags
let mut tags = gst::tags::TagList::new();
// Add a Title tag with the value "title"
tags.get_mut()
    .expect("Cannot get mutable reference to `tags`")
    .add::<gst::tags::Title>("title", gst::TagMergeMode::Append);

// Add the TagsList to the buffer's TagsMeta
let frame_meta_mut = frame_meta_buffer
    .get_mut()
    .expect("Could not add tags to `frame_meta_buffer`");
TagsMeta::add(frame_meta_mut, &mut tags);
```

Using the `BufferMeta` is very similar. Please see [src/rgbd/buffer.rs](src/buffer.rs) for examples.

### Read a Tag from a buffer

This example demonstrates how to read the Title tag from a buffer. Doing so sadly still requires some unsafe code. We have plans to wrap that in a safe API, but have not gotten around to do so yet.

```rust
// Assume that buffer is a tagged buffer

// Get the TagsMeta on the buffer and the TagsList stored inside it.
let meta = buffer
    .get_meta::<TagsMeta>()
    .unwrap();
let tag_list = unsafe { gst::tags::TagList::from_glib_none(meta.tags) };

// Get the Title tag from the TagList
let gst_tag_title =
    &tag_list
    .get::<gst::tags::Title>()
    .unwrap();
let title = gst_tag_title.get::<&str>().unwrap();
```

# Contributing

Please see [the contribution guidelines](CONTRIBUTING.md) for instructions on how to contribute.

# License

This project is licensed under the [Apache Version 2 license](LICENSE). Copyright 2019 Aivero.
