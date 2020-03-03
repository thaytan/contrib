use crate::buffer::BufferMeta;
use crate::tags::TagsMeta;

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
    for i in 0..remaining_buffers.len() {
        BufferMeta::add(main_buffer, &mut remaining_buffers[i]);
    }

    // Return Ok() if everything went fine
    Ok(())
}
