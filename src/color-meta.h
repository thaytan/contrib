#pragma once

#include <gst/gst.h>
#include <gst/gstmeta.h>
#include <gst/video/video.h>

G_BEGIN_DECLS

typedef struct _ColorMeta ColorMeta;

struct _ColorMeta {
  GstMeta meta;
  GstBuffer *color_buf;
};

GType color_meta_api_get_type(void);
const GstMetaInfo *color_meta_get_info(void);
ColorMeta *color_meta_get(GstBuffer *buf);
ColorMeta *color_meta_add(GstBuffer *buf);

G_END_DECLS
