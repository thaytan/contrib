#include "buffer-meta.h"

GType buffer_meta_api_get_type(void) {
    static volatile GType type;
    static const gchar *tags[] = {NULL};

    if (g_once_init_enter(&type)) {
        GType _type = gst_meta_api_type_register("BufferMetaAPI", tags);
        g_once_init_leave(&type, _type);
    }
    return type;
}

gboolean buffer_meta_init(GstMeta *meta, gpointer params, GstBuffer *buffer) {
    return TRUE;
}

gboolean buffer_meta_transform(GstBuffer *dest_buf, GstMeta *src_meta,
                               GstBuffer *src_buf, GQuark type, gpointer data) {
    BufferMeta *dest = buffer_meta_add(dest_buf);
    BufferMeta *src = (BufferMeta *) src_meta;

    dest->buffer = src->buffer;

    return TRUE;
}

void buffer_meta_free(GstMeta *meta, GstBuffer *buffer) {
    BufferMeta *local_meta = (BufferMeta *) meta;
    gst_buffer_unref(local_meta->buffer);
}

const GstMetaInfo *buffer_meta_get_info(void) {
    static const GstMetaInfo *meta_info = NULL;

    if (g_once_init_enter(&meta_info)) {
        const GstMetaInfo *meta = gst_meta_register(
                buffer_meta_api_get_type(), "BufferMeta", sizeof(BufferMeta),
                (GstMetaInitFunction) buffer_meta_init,
                (GstMetaFreeFunction) NULL,
                (GstMetaTransformFunction) buffer_meta_transform);
        g_once_init_leave(&meta_info, meta);
    }
    return meta_info;
}

BufferMeta *buffer_meta_get(GstBuffer *buf) {
    return ((BufferMeta *) gst_buffer_get_meta(buf, buffer_meta_api_get_type()));
}

BufferMeta *buffer_meta_add(GstBuffer *buf) {
    return ((BufferMeta *) gst_buffer_add_meta(buf, buffer_meta_get_info(), NULL));
}

