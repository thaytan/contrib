#pragma once

#include <gst/gst.h>
#include <gst/gstmeta.h>
#include <gst/gsttaglist.h>
#include <gst/video/video.h>

G_BEGIN_DECLS

typedef struct _BufferMeta BufferMeta;

struct _BufferMeta {
  GstMeta meta;
  GstBuffer *buffer;
  GstTagList *tags;
};

GType buffer_meta_api_get_type(void);
const GstMetaInfo *buffer_meta_get_info(void);
BufferMeta *buffer_meta_get(GstBuffer *buf);
BufferMeta *buffer_meta_add(GstBuffer *buf);

G_END_DECLS
