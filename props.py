import bpy
import blender_uv_exporter.ui
import bmesh


def get_attribute_items(attribute, context):
    items = []

    entry = blender_uv_exporter.ui.get_current_entry(context)

    if entry:
        if len(entry.objects) > 0:
            depsgraph = bpy.context.evaluated_depsgraph_get()
            obj = entry.objects[0].object
            bm = bmesh.new()
            bm.from_object(obj, depsgraph)
            bm.verts.ensure_lookup_table()

            for attribute in bm.verts.layers.float_color:
                if attribute.name[0] == ".":
                    continue
                items.append((attribute.name, attribute.name, attribute.name))

            bm.free()

    return items


class UVExporterObject(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(
        name="Object", type=bpy.types.Object
    )  # type: ignore


class UVExporterAttribute(bpy.types.PropertyGroup):
    target_channel: bpy.props.EnumProperty(
        name="Target Channel",
        items=[
            ("0", "UV0", "UV Channel"),
            ("1", "UV1", "UV Channel"),
            ("2", "UV2", "UV Channel"),
            ("3", "UV3", "UV Channel"),
        ],
        default="1",
    )  # type: ignore
    attribute: bpy.props.EnumProperty(
        name="Attribute", items=get_attribute_items
    )  # type: ignore


class UVExporterEntry(bpy.types.PropertyGroup):
    label: bpy.props.StringProperty(name="Label")  # type: ignore
    objects: bpy.props.CollectionProperty(
        name="Objects", type=UVExporterObject
    )  # type: ignore
    objects_index: bpy.props.IntProperty()  # type: ignore
    source_uv: bpy.props.EnumProperty(
        name="Index Channel",
        description="The UV channel that will be used to record vertex IDs.",
        items=[
            ("0", "UV0", "UV Channel"),
            ("1", "UV1", "UV Channel"),
            ("2", "UV2", "UV Channel"),
            ("3", "UV3", "UV Channel"),
        ],
        default="1",
    )  # type: ignore
    attributes: bpy.props.CollectionProperty(type=UVExporterAttribute)  # type: ignore
    attributes_index: bpy.props.IntProperty()  # type: ignore


class UVExporterPackage(bpy.types.PropertyGroup):
    label: bpy.props.StringProperty(name="Label")  # type: ignore
    path: bpy.props.StringProperty(name="Path", subtype="FILE_PATH", default="//")  # type: ignore
    entries: bpy.props.CollectionProperty(type=UVExporterEntry)  # type: ignore
    entries_index: bpy.props.IntProperty()  # type: ignore


scene_props = {}

scene_props["uv_exporter_packages"] = bpy.props.CollectionProperty(
    name="Packages", description="A list of packages", type=UVExporterPackage
)

scene_props["uv_exporter_packages_index"] = bpy.props.IntProperty(
    name="Objects index", description="Object list index"
)


def register():
    for id, prop in scene_props.items():
        setattr(bpy.types.Scene, id, prop)


def unregister():
    for id, prop in scene_props.items():
        delattr(bpy.types.Scene, id)
