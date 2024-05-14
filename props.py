import bpy

def get_attribute_items(attribute, context):
    items = [

    ]

    if context.scene.uv_exporter_objects_index >= 0 and context.scene.uv_exporter_objects:
        obj = context.scene.uv_exporter_objects[context.scene.uv_exporter_objects_index]
        for attribute in obj.object.data.attributes:
            if attribute.name[0] == '.':
                continue
            if attribute.data_type != 'FLOAT_COLOR':
                continue
            if attribute.domain != 'POINT':
                continue
            items.append((attribute.name, attribute.name, attribute.name))

    return items
class UVExporterAttribute(bpy.types.PropertyGroup):
    target_channel: bpy.props.EnumProperty(
        name = "Target Channel",
        items = [
            ("0", "UV0", "UV Channel"),
            ("1", "UV1", "UV Channel"),
            ("2", "UV2", "UV Channel"),
            ("3", "UV3", "UV Channel"),
        ]
    ) # type: ignore
    attribute: bpy.props.EnumProperty(
        name = "Attribute",
        items = get_attribute_items
    ) # type: ignore

class UVExporterObject(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(
        type = bpy.types.Object,
        name = "Object"
    ) # type: ignore
    source_uv: bpy.props.IntProperty(
        name = "Source UV Channel"
    ) # type: ignore
    items: bpy.props.CollectionProperty(
        type = UVExporterAttribute
    ) # type: ignore
    item_index: bpy.props.IntProperty(
        
    ) # type: ignore

scene_props = {}

scene_props["uv_exporter_objects"] = bpy.props.CollectionProperty(
    name = "Objects",
    description = "The objects to export attributes for",
    type = UVExporterObject
)

scene_props["uv_exporter_objects_index"] = bpy.props.IntProperty(
    name = "Objects index",
    description = "Object list index"
)


def register():
    for id, prop in scene_props.items():
        setattr(bpy.types.Scene, id, prop)

def unregister():
    for id, prop in scene_props.items():
        delattr(bpy.types.Scene, id)