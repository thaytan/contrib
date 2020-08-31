use crate::buffer::BufferMeta;
use crate::tags::TagsMeta;
use crate::RgbdError;
use glib::value::FromValueOptional;

/// Fill the `main_buffer` with `buffer` and mark it appropriately with `tag`.
///
/// # Arguments
/// * `main_buffer` - Output buffer that will be tagged and contain `buffer` after this function gets executed.
/// * `buffer` - Buffer containing the data.
/// * `tag` - Tag of the buffer.
///
/// # Returns
/// * `Ok()` on success.
/// * `Err(gst::ErrorMessage)` on failure, occurs only if mutable references to tags/buffer cannot be obtained.
pub fn fill_main_buffer_and_tag(
    main_buffer: &mut gst::Buffer,
    buffer: gst::Buffer,
    tag: &str,
) -> Result<(), gst::ErrorMessage> {
    // Put the frame directly into the output buffer
    *main_buffer = buffer;

    // Tag the buffer appropriately
    tag_buffer(
        main_buffer.get_mut().ok_or(gst_error_msg!(
            gst::ResourceError::Failed,
            [
                "Cannot get mutable reference to the buffer for {} stream",
                tag
            ]
        ))?,
        tag,
    )?;

    // Return Ok() if everything went fine
    Ok(())
}

/// Attach the `buffer` to the `main_buffer` and mark it appropriately with `tag`.
///
/// # Arguments
/// * `main_buffer` - Output buffer that will have `buffer` attached to it after this function gets executed.
/// * `buffer` - Buffer containing the data, which will be tagged and attached to `main_buffer`.
/// * `tag` - Tag of the buffer.
///
/// # Returns
/// * `Ok()` on success.
/// * `Err(gst::ErrorMessage)` on failure, occurs only if mutable references to tags/buffer cannot be obtained.
pub fn attach_aux_buffer_and_tag(
    main_buffer: &mut gst::BufferRef,
    buffer: &mut gst::Buffer,
    tag: &str,
) -> Result<(), gst::ErrorMessage> {
    // Tag the buffer appropriately
    tag_buffer(
        buffer.get_mut().ok_or(gst_error_msg!(
            gst::ResourceError::Failed,
            [
                "Cannot get mutable reference to the buffer for {} stream",
                tag
            ]
        ))?,
        tag,
    )?;

    // Attach this new buffer as meta to the output buffer
    BufferMeta::add(main_buffer, buffer);

    // Return Ok() if everything went fine
    Ok(())
}

/// Get all auxiliary buffers attached to the `main_buffer`.
///
/// # Arguments
/// * `main_buffer` - The main buffer to remove auxiliary buffers from.
///
/// # Returns
/// * Vec<gst::Buffer> containing the immutable auxiliary buffers.
pub fn get_aux_buffers(main_buffer: &gst::Buffer) -> Vec<gst::Buffer> {
    main_buffer
        .iter_meta::<BufferMeta>()
        .map(|meta| unsafe { gst::buffer::Buffer::from_glib_none(meta.buffer) })
        .collect()
}

/// Get all auxiliary buffers attached to the `main_buffer`.
///
/// # Arguments
/// * `main_buffer` - The main buffer to remove auxiliary buffers from.
///
/// # Returns
/// * Vec<gst::Buffer> containing the mutable auxiliary buffers.
pub fn get_aux_buffers_mut(main_buffer: &mut gst::BufferRef) -> Vec<gst::Buffer> {
    main_buffer
        .iter_meta_mut::<BufferMeta>()
        .map(|meta| unsafe { gst::buffer::Buffer::from_glib_none(meta.buffer) })
        .collect()
}

/// Tag a `buffer` with `tag`.
///
/// # Arguments
/// * `buffer` - Buffer to be tagged.
/// * `tag` - The tag to assign to the buffer.
///
/// # Returns
/// * `Ok()` on success.
/// * `Err(gst::ErrorMessage)` on failure, occurs only if mutable references to tags cannot be obtained.
pub fn tag_buffer(buffer: &mut gst::BufferRef, tag: &str) -> Result<(), gst::ErrorMessage> {
    // Create an appropriate tag
    let mut tags = gst::tags::TagList::new();
    tags.get_mut()
        .ok_or(gst_error_msg!(
            gst::ResourceError::Failed,
            ["Cannot get mutable reference to {} tag", tag]
        ))?
        .add::<gst::tags::Title>(&tag, gst::TagMergeMode::Append);

    // Add the tag to the output buffer
    TagsMeta::add(buffer, &mut tags);

    // Return Ok() if everything went fine
    Ok(())
}

/// Get tag of the `buffer`.
///
/// # Arguments
/// * `buffer` - Buffer to read the tag from.
///
/// # Returns
/// * `Ok(&str)` with tag on success.
/// * `Err(gst::ErrorMessage)` on failure, if buffer has invalid tag.
pub fn get_tag(buffer: &gst::Buffer) -> Result<&str, gst::ErrorMessage> {
    // Get TagList from GstBuffer
    let tag_list = unsafe {
        gst::tags::TagList::from_glib_none(
            buffer
                .get_meta::<TagsMeta>()
                .ok_or(gst_error_msg!(
                    gst::ResourceError::Failed,
                    ["Buffer {:?} has no tags", buffer]
                ))?
                .tags,
        )
    };

    // Get the title tag from TagList
    let tag = tag_list.get::<gst::tags::Title>().ok_or(gst_error_msg!(
        gst::ResourceError::Failed,
        ["Buffer {:?} has no title tag", buffer]
    ))?;
    let tag = tag.get().ok_or(gst_error_msg!(
        gst::ResourceError::Failed,
        ["Buffer {:?} has invalid title tag", buffer]
    ))?;

    // Return it as string slice
    Ok(Box::leak(Box::from(tag)))
}

/// Remove all tags of a `buffer`.
///
/// # Arguments
/// * `buffer` - The buffer to remove the tags from.
pub fn clear_tags(buffer: &mut gst::BufferRef) {
    loop {
        let tag = buffer.get_meta_mut::<TagsMeta>();
        match tag {
            Some(t) => t.remove(),
            None => break,
        }
    }
}

/// Replaces all existing tags of `buffer` with `tag`.
///
/// # Arguments
/// * `buffer` - The buffer to remove the tags from.
/// * `tag` - The tag to assign to the buffer.
///
/// # Returns
/// * `Ok()` on success.
/// * `Err(gst::ErrorMessage)` on failure, occurs only if mutable references to tags cannot be obtained.
pub fn replace_tag(buffer: &mut gst::BufferRef, tag: &str) -> Result<(), gst::ErrorMessage> {
    // First remove all tags
    clear_tags(buffer);

    // Retag the buffer appropriately
    tag_buffer(buffer, tag)?;

    // Return Ok() if everything went fine
    Ok(())
}

/// Removes the specific auxiliary buffers attached to the `main_buffer` based on the specified `tags`.
///
/// # Arguments
/// * `main_buffer` - The main buffer to remove auxiliary buffers from.
/// * `tags` - The tags that specify what buffers to remove.
///
/// # Returns
/// * `Ok()` on success.
/// * `Err(gst::ErrorMessage)` on failure, occurs only if mutable references to tags cannot be obtained.
pub fn remove_aux_buffers_with_tags(
    main_buffer: &mut gst::BufferRef,
    tags: &[&str],
) -> Result<(), gst::ErrorMessage> {
    // Allocate a vector for saving the buffers that should not be removed
    let mut remaining_buffers: Vec<gst::Buffer> = vec![];

    // Loop over all auxiliary buffers
    #[allow(clippy::while_let_loop)]
    loop {
        // Check if there are any auxiliary buffers left, break if not
        let meta = match main_buffer.get_meta_mut::<BufferMeta>() {
            Some(meta) => meta,
            None => break,
        };
        let auxiliary_buffer = unsafe { gst::buffer::Buffer::from_glib_none(meta.buffer) };

        if tags.contains(&get_tag(&auxiliary_buffer)?) {
            // Remove buffers with the corresponding tags
            meta.remove();
        } else {
            // Keep buffers that do not match the tag
            remaining_buffers.push(auxiliary_buffer);
            // Remove it from the list, so that it can be reattached again
            meta.remove();
        }
    }

    // Return the remaining buffers back
    for buffer in &mut remaining_buffers {
        BufferMeta::add(main_buffer, buffer);
    }

    // Return Ok() if everything went fine
    Ok(())
}

/// Gets the field with the given `name` of type `T` in the given CAPS `structure`.
/// # Arguments
/// * `structure` - The structure to read the field from.
/// * `name` - The name of the field to get.
/// * `type_` - The name of `T` in string format. Solely used for error formatting.
/// # Returns
/// * `Ok(T)` - If the field exists and is of type `T`.
/// * `Err(RgbdError::MissingCapsField)` - If `structure` does not have a field called `name`.
/// * `Err(RgbdError::WrongCapsFormat)` - If the field is not of type `T`.
pub fn get_field<'structure, T: FromValueOptional<'structure>>(
    structure: &'structure gst::StructureRef,
    name: &str,
    type_: &'static str,
) -> Result<T, RgbdError> {
    let value = structure
        .get::<T>(name)
        .map_err(|_| RgbdError::WrongCapsFormat {
            name: name.to_string(),
            type_,
        })?
        .ok_or_else(|| RgbdError::MissingCapsField(name.to_string()))?;
    Ok(value)
}

/// Converts the given `caps` and `framerate` into a `gst::VideoInfo` for the stream with the given
/// name.
/// # Arguments
/// * `caps` - The caps to convert.
/// * `framerate` - The framerate of the stream.
/// # Returns
/// * `Ok(VideoInfo)` - If the CAPS were successfully converted.
/// * `Err(RgbdError::MissingCapsField)` - If any required fields on the CAPS do not exist.
/// * `Err(RgbdError::WrongCapsFormat)` - If a field on the CAPS are not of correct type.
/// * `Err(RgbdError::NoVideoInfo)` - If `caps` could not be converted into `VideoInfo`.
pub fn get_video_info(
    caps: &gst::StructureRef,
    stream_name: &str,
) -> Result<gstreamer_video::VideoInfo, RgbdError> {
    let framerate = get_field::<gst::Fraction>(caps, "framerate", "Fraction")?;
    let stream_width = get_field::<i32>(caps, &format!("{}_width", stream_name), "i32")?;
    let stream_height = get_field::<i32>(caps, &format!("{}_height", stream_name), "i32")?;
    let stream_format = get_field::<&str>(caps, &format!("{}_format", stream_name), "str")?;

    gstreamer_video::VideoInfo::builder(
        stream_format.parse().map_err(|_| RgbdError::NoVideoInfo)?,
        stream_width as u32,
        stream_height as u32,
    )
    .fps(framerate)
    .build()
    .map_err(|_| RgbdError::NoVideoInfo)
}

/// Aligns `buffer` to u16, such that it can be used to store depth video.
/// # Arguments
/// * `buffer` - The buffer to convert to depth.
/// # Returns
/// * `Ok` - If the buffer is properly aligned to u16.
/// * `Err` - If not.
pub fn to_depth_buffer(buffer: &[u8]) -> Result<&[u16], RgbdError> {
    let (head, in_data_u16, tail) = unsafe { buffer.align_to::<u16>() };
    // Ensure that the frame's byte was correctly aligned to a u16 slice. If head or tail is
    // non-empty, it means that the buffer was not correctly aligned and we therefore return an
    // error.
    if !head.is_empty() || !tail.is_empty() {
        return Err(RgbdError::BufferNotAligned);
    }
    Ok(in_data_u16)
}

pub fn to_depth_buffer_mut(buffer: &mut [u8]) -> Result<&mut [u16], RgbdError> {
    let (head, in_data_u16, tail) = unsafe { buffer.align_to_mut::<u16>() };
    // Ensure that the frame's byte was correctly aligned to a u16 slice. If head or tail is
    // non-empty, it means that the buffer was not correctly aligned and we therefore return an
    // error.
    if !head.is_empty() || !tail.is_empty() {
        return Err(RgbdError::BufferNotAligned);
    }
    Ok(in_data_u16)
}

#[cfg(test)]
mod tests {
    use super::*;
    use gst::Buffer;

    #[test]
    fn new_buffer_no_tag() {
        gst::init().unwrap();

        let buffer = Buffer::new();

        // Make sure there is no tag in a new buffer
        assert!(get_tag(&buffer).is_err());
    }

    #[test]
    fn beffer_tag() {
        gst::init().unwrap();

        let mut buffer = Buffer::new();
        let original_tag = "depth";

        // Create main buffer with a tag
        tag_buffer(buffer.get_mut().unwrap(), original_tag).unwrap();

        // Extract the tag from the buffer
        let tag = get_tag(&buffer).unwrap();

        // Make sure the tag stayed the same
        assert_eq!(tag, original_tag);
    }

    #[test]
    fn main_buffer_tag() {
        gst::init().unwrap();

        let mut main_buffer = Buffer::new();
        let buffer = Buffer::new();
        let original_tag = "depth";

        // Create main buffer with a tag
        fill_main_buffer_and_tag(&mut main_buffer, buffer, original_tag).unwrap();

        // Extract the tag from the buffer
        let tag = get_tag(&main_buffer).unwrap();

        // Make sure the tag stayed the same
        assert_eq!(tag, original_tag);
    }

    #[test]
    fn aux_buffers_tag() {
        gst::init().unwrap();

        let mut main_buffer = Buffer::new();
        let mut buffer_depth = Buffer::new();
        let mut buffer_color = Buffer::new();
        let original_tag_depth = "depth";
        let original_tag_color = "color";

        // Attach buffers to the main buffer
        attach_aux_buffer_and_tag(
            main_buffer.get_mut().unwrap(),
            &mut buffer_depth,
            original_tag_depth,
        )
        .unwrap();
        attach_aux_buffer_and_tag(
            main_buffer.get_mut().unwrap(),
            &mut buffer_color,
            original_tag_color,
        )
        .unwrap();

        // Get the auxiliary buffers
        let aux_buffers = get_aux_buffers(&main_buffer);

        // Make sure the length is correct
        assert_eq!(aux_buffers.len(), 2);

        // Extract the tag from the buffer
        let tag_depth = get_tag(&aux_buffers[0]).unwrap();
        let tag_color = get_tag(&aux_buffers[1]).unwrap();

        // Make sure the tags stayed the same
        assert_eq!(tag_depth, original_tag_depth);
        assert_eq!(tag_color, original_tag_color);
    }

    #[test]
    fn tag_clearing() {
        gst::init().unwrap();

        let mut buffer = Buffer::new();
        let original_tag = "depth";

        // Create main buffer with a tag
        tag_buffer(buffer.get_mut().unwrap(), original_tag).unwrap();

        // Extract the tag from the buffer
        let tag = get_tag(&buffer).unwrap();

        // Make sure the tag stayed the same
        assert_eq!(tag, original_tag);

        clear_tags(buffer.get_mut().unwrap());

        // Make sure there is no tag anymore
        assert!(get_tag(&buffer).is_err());
    }

    #[test]
    fn tag_replace() {
        gst::init().unwrap();

        let mut buffer = Buffer::new();
        let original_tag = "depth";
        let new_tag = "color";

        // Create main buffer with a tag
        tag_buffer(buffer.get_mut().unwrap(), original_tag).unwrap();

        // Extract the tag from the buffer
        let tag = get_tag(&buffer).unwrap();

        // Make sure the tag stayed the same
        assert_eq!(tag, original_tag);

        replace_tag(buffer.get_mut().unwrap(), new_tag).unwrap();

        // Extract the tag from the buffer again
        let tag = get_tag(&buffer).unwrap();

        // Make sure the tag changed
        assert_eq!(tag, new_tag);
    }

    #[test]
    fn remove_specific_aux_buffers() {
        gst::init().unwrap();

        let mut main_buffer = Buffer::new();
        let mut buffer_depth = Buffer::new();
        let mut buffer_color = Buffer::new();
        let mut buffer_infra = Buffer::new();
        let original_tag_depth = "depth";
        let original_tag_color = "color";
        let original_tag_infra = "infra";

        // Attach buffers to the main buffer
        attach_aux_buffer_and_tag(
            main_buffer.get_mut().unwrap(),
            &mut buffer_depth,
            original_tag_depth,
        )
        .unwrap();
        attach_aux_buffer_and_tag(
            main_buffer.get_mut().unwrap(),
            &mut buffer_color,
            original_tag_color,
        )
        .unwrap();
        attach_aux_buffer_and_tag(
            main_buffer.get_mut().unwrap(),
            &mut buffer_infra,
            original_tag_infra,
        )
        .unwrap();

        // Get the auxiliary buffers
        let aux_buffers = get_aux_buffers(&main_buffer);

        // Make sure the length is correct
        assert_eq!(aux_buffers.len(), 3);

        // Extract the tag from the buffer
        let tag_depth = get_tag(&aux_buffers[0]).unwrap();
        let tag_color = get_tag(&aux_buffers[1]).unwrap();
        let tag_infra = get_tag(&aux_buffers[2]).unwrap();

        // Make sure the tags stayed the same
        assert_eq!(tag_depth, original_tag_depth);
        assert_eq!(tag_color, original_tag_color);
        assert_eq!(tag_infra, original_tag_infra);

        // Remove depth and color
        remove_aux_buffers_with_tags(
            main_buffer.get_mut().unwrap(),
            &[original_tag_color, original_tag_depth],
        )
        .unwrap();

        // Get the auxiliary buffers
        let aux_buffers = get_aux_buffers(&main_buffer);

        // Make sure the length is correct
        assert_eq!(aux_buffers.len(), 1);

        // Make sure the correct buffer remains (infra)
        let tag_infra = get_tag(&aux_buffers[0]).unwrap();
        assert_eq!(tag_infra, original_tag_infra);
    }
}
