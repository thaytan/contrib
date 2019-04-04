#include "color-meta.h"

GType color_meta_api_get_type(void) {
    static volatile GType type;
    static const gchar *tags[] = {NULL};

    if (g_once_init_enter(&type)) {
        GType _type = gst_meta_api_type_register("ColorMetaAPI", tags);
        g_once_init_leave(&type, _type);
    }
    return type;
}

gboolean color_meta_init(GstMeta *meta, gpointer params, GstBuffer *buffer) {
    return TRUE;
}

gboolean color_meta_transform(GstBuffer *dest_buf, GstMeta *src_meta,
                              GstBuffer *src_buf, GQuark type, gpointer data) {
    ColorMeta *dest_color = color_meta_add(dest_buf);
    ColorMeta *src_color = (ColorMeta *) src_meta;

    dest_color->color_buf = src_color->color_buf;

    return TRUE;
}

void color_meta_free(GstMeta *meta, GstBuffer *buffer) {
    ColorMeta *local_meta = (ColorMeta *) meta;
    gst_buffer_unref(local_meta->color_buf);
}

const GstMetaInfo *color_meta_get_info(void) {
    static const GstMetaInfo *meta_info = NULL;

    if (g_once_init_enter(&meta_info)) {
        const GstMetaInfo *meta = gst_meta_register(
                color_meta_api_get_type(), "ColorMeta", sizeof(ColorMeta),
                (GstMetaInitFunction) color_meta_init,
                (GstMetaFreeFunction) NULL,
                (GstMetaTransformFunction) color_meta_transform);
        g_once_init_leave(&meta_info, meta);
    }
    return meta_info;
}

ColorMeta *color_meta_get(GstBuffer *buf) {
    return ((ColorMeta *) gst_buffer_get_meta(buf, color_meta_api_get_type()));
}

ColorMeta *color_meta_add(GstBuffer *buf) {
    return ((ColorMeta *) gst_buffer_add_meta(buf, color_meta_get_info(), NULL));
}

