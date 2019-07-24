#include "gstcolorizer.h"

#include <gst/video/video.h>

#define DEFAULT_PROP_PRESET GST_COLORIZER_PRESET_JET

GST_DEBUG_CATEGORY_STATIC(colorizer_debug);
#define GST_CAT_DEFAULT (colorizer_debug)

enum { PROP_0, PROP_PRESET };

#define gst_colorizer_parent_class parent_class
G_DEFINE_TYPE(GstColorizer, gst_colorizer, GST_TYPE_VIDEO_FILTER);

static GstStaticPadTemplate gst_colorizer_src_template =
    GST_STATIC_PAD_TEMPLATE("src", GST_PAD_SRC, GST_PAD_ALWAYS,
                            GST_STATIC_CAPS(GST_VIDEO_CAPS_MAKE("{ RGB }")));

static GstStaticPadTemplate gst_colorizer_sink_template =
    GST_STATIC_PAD_TEMPLATE(
        "sink", GST_PAD_SINK, GST_PAD_ALWAYS,
        GST_STATIC_CAPS(GST_VIDEO_CAPS_MAKE("{ GRAY16_LE }")));

#define GST_TYPE_COLORIZER_PRESET (gst_colorizer_preset_get_type())
static GType gst_colorizer_preset_get_type(void) {
  static GType preset_type = 0;

  static const GEnumValue presets[] = {
      {GST_COLORIZER_PRESET_NONE, "Do not apply anything", "none"},
      {GST_COLORIZER_PRESET_JET, "Apply jet color map to image", "jet"},
      {0, NULL, NULL},
  };

  if (!preset_type) {
    preset_type = g_enum_register_static("GstColorizerPreset", presets);
  }
  return preset_type;
}

static GstFlowReturn gst_colorizer_transform_gray16(GstColorizer *filter,
                                                    GstVideoFrame *inframe,
                                                    GstVideoFrame *outframe) {
  if (!filter->table) {
    return GST_FLOW_OK;
  }

  gint width = GST_VIDEO_FRAME_WIDTH(outframe);
  gint height = GST_VIDEO_FRAME_HEIGHT(outframe);

  guint16 *in = (guint16 *)inframe->data[0];
  guint8 *out = (guint8 *)outframe->data[0];

  for (guint i = 0; i < width * height; i++) {
    guint16 gray = in[i];
    out[i * 3 + 0] = filter->table[gray * 3 + 0];
    out[i * 3 + 1] = filter->table[gray * 3 + 1];
    out[i * 3 + 2] = filter->table[gray * 3 + 2];
  }

  return GST_FLOW_OK;
}

static gboolean gst_colorizer_set_info(GstVideoFilter *vfilter, GstCaps *incaps,
                                       GstVideoInfo *in_info, GstCaps *outcaps,
                                       GstVideoInfo *out_info) {
  GstColorizer *filter = GST_COLORIZER(vfilter);

  GST_DEBUG_OBJECT(filter, "in %" GST_PTR_FORMAT " out %" GST_PTR_FORMAT,
                   incaps, outcaps);

  filter->process = NULL;

  filter->info = out_info;
  filter->format = GST_VIDEO_INFO_FORMAT(in_info);
  filter->width = GST_VIDEO_INFO_WIDTH(in_info);
  filter->height = GST_VIDEO_INFO_HEIGHT(in_info);

  GST_OBJECT_LOCK(filter);

  switch (filter->format) {
    case GST_VIDEO_FORMAT_GRAY16_LE:
      filter->process = gst_colorizer_transform_gray16;
      break;
    default:
      break;
  }

  GST_OBJECT_UNLOCK(filter);

  return filter->process != NULL;
}

double clamp(double v) {
  const double t = v < 0 ? 0 : v;
  return t > 1.0 ? 1.0 : t;
}

guint8 *generate_map(GstColorizer *filter, GstColorizerPreset preset) {
  if (!preset) {
    return NULL;
  } else if (preset == GST_COLORIZER_PRESET_JET) {
    filter->table = malloc(sizeof(guint8) * 3 * 65536);
    for (guint16 i = 0; i < 65535; i++) {
      double t = (i * 2.0 / 65535) - 1;
      double red = clamp(1.5 - ABS(2.0 * t - 1.0));
      double green = clamp(1.5 - ABS(2.0 * t));
      double blue = clamp(1.5 - ABS(2.0 * t + 1.0));
      filter->table[i * 3 + 0] = red * 255;
      filter->table[i * 3 + 1] = green * 255;
      filter->table[i * 3 + 2] = blue * 255;
    }
  } else {
    g_assert_not_reached();
  }
}

static void gst_colorizer_set_property(GObject *object, guint prop_id,
                                       const GValue *value, GParamSpec *pspec) {
  GstColorizer *filter = GST_COLORIZER(object);

  switch (prop_id) {
    case PROP_PRESET:
      GST_OBJECT_LOCK(filter);
      filter->preset = g_value_get_enum(value);
      filter->table = generate_map(filter, filter->preset);
      GST_OBJECT_UNLOCK(filter);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID(object, prop_id, pspec);
      break;
  }
}

static void gst_colorizer_get_property(GObject *object, guint prop_id,
                                       GValue *value, GParamSpec *pspec) {
  GstColorizer *filter = GST_COLORIZER(object);

  switch (prop_id) {
    case PROP_PRESET:
      GST_OBJECT_LOCK(filter);
      g_value_set_enum(value, filter->preset);
      GST_OBJECT_UNLOCK(filter);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID(object, prop_id, pspec);
      break;
  }
}

static GstCaps *gst_colorizer_transform_caps(GstBaseTransform *trans,
                                             GstPadDirection direction,
                                             GstCaps *caps, GstCaps *filter) {
  GstCaps *other_caps = gst_caps_copy(caps);
  gsize caps_size = gst_caps_get_size(other_caps);

  for (gsize i = 0; i < caps_size; i++) {
    GstStructure *structure = gst_caps_get_structure(other_caps, i);

    if (direction == GST_PAD_SRC) {
      gst_structure_set_name(structure, "video/x-raw");
      GValue gvalue = G_VALUE_INIT;
      g_value_init(&gvalue, G_TYPE_STRING);
      g_value_set_string(&gvalue, "GRAY16_LE");
      gst_structure_set_value(structure, "format", &gvalue);
    } else {
      gst_structure_set_name(structure, "video/x-raw");
      GValue gvalue = G_VALUE_INIT;
      g_value_init(&gvalue, G_TYPE_STRING);
      g_value_set_string(&gvalue, "RGB");
      gst_structure_set_value(structure, "format", &gvalue);
    }
  }

  if (filter) {
    return gst_caps_intersect_full(filter, other_caps,
                                   GST_CAPS_INTERSECT_FIRST);
  } else {
    return other_caps;
  }
}

static void gst_colorizer_class_init(GstColorizerClass *klass) {
  GObjectClass *gobject_class = (GObjectClass *)klass;
  GstElementClass *element_class = (GstElementClass *)klass;
  GstVideoFilterClass *vfilter_class = (GstVideoFilterClass *)klass;
  GstBaseTransformClass *base_transform_class = GST_BASE_TRANSFORM_CLASS(klass);

  GST_DEBUG_CATEGORY_INIT(colorizer_debug, "colorizer", 0, "colorizer");

  base_transform_class->transform_caps = gst_colorizer_transform_caps;

  gobject_class->set_property = gst_colorizer_set_property;
  gobject_class->get_property = gst_colorizer_get_property;

  g_object_class_install_property(
      gobject_class, PROP_PRESET,
      g_param_spec_enum("preset", "Preset", "Color effect preset to use",
                        GST_TYPE_COLORIZER_PRESET, DEFAULT_PROP_PRESET,
                        G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS));

  vfilter_class->set_info = GST_DEBUG_FUNCPTR(gst_colorizer_set_info);
  vfilter_class->transform_frame =
      GST_DEBUG_FUNCPTR(gst_colorizer_transform_gray16);

  gst_element_class_set_static_metadata(
      element_class, "Grayscale colorizer", "Filter/Effect/Video",
      "Grayscale colorizer", "Aivero AS <code@aivero.com>");

  gst_element_class_add_static_pad_template(element_class,
                                            &gst_colorizer_sink_template);
  gst_element_class_add_static_pad_template(element_class,
                                            &gst_colorizer_src_template);
}

static void gst_colorizer_init(GstColorizer *filter) {
  filter->preset = GST_COLORIZER_PRESET_JET;
  filter->table = NULL;
}

static gboolean plugin_init(GstPlugin *plugin) {
  gst_element_register(plugin, "gstcolorizer", GST_RANK_NONE,
                       gst_colorizer_preset_get_type());
  return TRUE;
}