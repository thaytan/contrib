#pragma once

#include <gst/gst.h>
#include <gst/gstmeta.h>
#include <gst/gsttaglist.h>
#include <gst/video/video.h>

G_BEGIN_DECLS

typedef struct _FrameMeta FrameMeta;

struct _FrameMeta {
    GstMeta meta;
    u_int8_t *bytes;
    size_t nbytes;
};

GType frame_meta_api_get_type(void);
const GstMetaInfo *frame_meta_get_info(void);
FrameMeta *frame_meta_get(GstBuffer *buffer);
FrameMeta *frame_meta_add(GstBuffer *buffer, u_int8_t *bytes, size_t nbytes);

G_END_DECLS
