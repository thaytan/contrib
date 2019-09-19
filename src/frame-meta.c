#include "frame-meta.h"

GType frame_meta_api_get_type(void) {
    static volatile GType type;
    static const gchar *tags[] = {NULL};

    if (g_once_init_enter(&type)) {
        GType _type = gst_meta_api_type_register("FrameMetaAPI", tags);
        g_once_init_leave(&type, _type);
    }
    return type;
}

gboolean frame_meta_init(GstMeta *meta, gpointer params, GstBuffer *buffer) {
    return TRUE;
}

gboolean frame_meta_transform(GstBuffer *dest_buf, GstMeta *src_meta,
                             GstBuffer *src_buf, GQuark type, gpointer data) {
    FrameMeta *src = (FrameMeta *) src_meta;
    frame_meta_add(dest_buf, src->tags);

    return TRUE;
}

void frame_meta_free(GstMeta *meta, GstBuffer *buffer) {
    FrameMeta *local_meta = (FrameMeta *) meta;
    free(local_meta->bytes);
}

const GstMetaInfo *frame_meta_get_info(void) {
    static const GstMetaInfo *meta_info = NULL;

    if (g_once_init_enter(&meta_info)) {
        const GstMetaInfo *meta = gst_meta_register(
                frame_meta_api_get_type(), "FrameMeta", sizeof(FrameMeta),
                (GstMetaInitFunction) frame_meta_init,
                (GstMetaFreeFunction) frame_meta_free,
                (GstMetaTransformFunction) frame_meta_transform);
        g_once_init_leave(&meta_info, meta);
    }
    return meta_info;
}

FrameMeta *frame_meta_get(GstBuffer *buffer) {
    g_return_val_if_fail(GST_IS_BUFFER(buffer), NULL);

    return ((FrameMeta *) gst_buffer_get_meta(buffer, frame_meta_api_get_type()));
}

int * intdup(u_int8_t const * src, size_t len)
{
    int * p = malloc(len * sizeof(u_int8_t));
    memcpy(p, src, len * sizeof(u_int8_t));
    return p;
}

FrameMeta *frame_meta_add(GstBuffer *buffer, u_int8_t *bytes, size_t nbytes) {
    FrameMeta *meta;

    g_return_val_if_fail(GST_IS_BUFFER (buffer), NULL);

    meta = (FrameMeta *) gst_buffer_add_meta(buffer, frame_meta_get_info(), NULL);

    if (!meta)
        return NULL;

    // We copy the array, as I'm not sure whether Rust will deallocate the array after the invocation
    meta->bytes = intdup(bytes, nbytes);

    return meta;
}
