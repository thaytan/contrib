use std::fmt;

use gst::meta::*;
use gst::BufferRef;
use gst::MiniObject;

use glib;
use glib::translate::from_glib;

use crate::sys;
pub use crate::sys::TagsMeta;

/// The TagsMeta API is intended to allow developers to add Tags onto gst buffers, which can be used
/// to identify different buffers from each other.
impl TagsMeta {
    /// Adds a TagList as metadata onto the given `buffer`.
    /// # Arguments
    /// * `buffer` - The buffer onto which the TagList should be added.
    /// * `meta_tags` - The TagsList that should be added as metadata.
    /// # Example
    /// ```
    /// use gstreamer_depth_meta::tags::TagsMeta;
    /// gstreamer::init().unwrap();
    /// let mut main_buffer = gstreamer::Buffer::new();
    /// let mut tags = gstreamer::tags::TagList::new();
    /// tags.get_mut().unwrap()
    ///     .add::<gstreamer::tags::Title>(&"example-tag", gstreamer::TagMergeMode::Append);
    /// TagsMeta::add(
    ///    main_buffer.make_mut(),
    ///    &mut tags,
    /// );
    /// ```
    pub fn add<'a>(
        buffer: &'a mut BufferRef,
        meta_tags: &mut gst::TagList,
    ) -> MetaRefMut<'a, Self, Standalone> {
        unsafe {
            let meta = sys::tags_meta_add(buffer.as_mut_ptr(), meta_tags.as_mut_ptr());
            Self::from_mut_ptr(buffer, meta)
        }
    }

    /// Gets the first [TagsMeta](struct.TagsMeta.html) attached onto the given `buffer`.
    /// # Arguments
    /// * `buffer` - A reference to the buffer, from which the [TagsMeta](struct.TagsMeta.html) should be read.
    pub fn get(buffer: &mut BufferRef) -> &TagsMeta {
        unsafe { &*sys::tags_meta_get(buffer.as_mut_ptr()) }
    }
}

unsafe impl MetaAPI for TagsMeta {
    type GstType = TagsMeta;

    fn get_meta_api() -> glib::Type {
        unsafe { from_glib(sys::tags_meta_api_get_type()) }
    }
}

impl fmt::Debug for TagsMeta {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        f.debug_struct("TagsMeta")
            .field("tags", &self.tags)
            .finish()
    }
}

mod tests {
    use super::*;

    fn get_tags(tag: &str) -> gst::TagList {
        let mut tags = gst::tags::TagList::new();
        tags.get_mut().unwrap().add::<gst::tags::Title>(&tag, gst::TagMergeMode::Append);
        tags
    }

    #[test]
    fn add_and_get_expect_tags_equal() {
        // Arrange
        gst::init().unwrap();
        let input_title = "example-tag";
        let mut buffer = gst::Buffer::new();
        let mut tags = get_tags(input_title);

        // Act
        TagsMeta::add(buffer.make_mut(), &mut tags);

        // Assert
        // convert get the Title tag from the MetaAPI
        let meta = TagsMeta::get(buffer.get_mut().unwrap());
        let tag_list = unsafe { gst::tags::TagList::from_glib_none(meta.tags) };

        // Get the tag title from GstTagList
        let gst_tag_title = &tag_list.get::<gst::tags::Title>().unwrap();
        let title = gst_tag_title.get().unwrap();

        assert_eq!(input_title, title);
    }

    #[test]
    fn add_and_remove_expect_no_tags_present() {
        // Arrange
        gst::init().unwrap();
        let input_title = "example-tag";
        let mut buffer = gst::Buffer::new();
        let mut tags = get_tags(input_title);
        let tags_meta = TagsMeta::add(buffer.make_mut(), &mut tags);

        // Act
        tags_meta.remove();

        // Assert
        for i in buffer.iter_meta::<TagsMeta>() {
            assert_eq!(true, false, "A TagsMeta was still present on the buffer: {:#?}", i)
        }
    }
}