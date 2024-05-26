from typing import Iterator, List
import bmesh
import bpy

from .context_managers import EnsureGeonodes

from . import ui


def refresh_attribute_choices(self, context) -> None:
    entry = ui.get_current_entry(context)

    if entry:
        context.scene.attribute_choices.clear()

        objects = entry.get_objects()

        if len(objects) > 0:
            obj = objects[0]
            print(obj)

            with EnsureGeonodes(context, [obj]):
                depsgraph = bpy.context.evaluated_depsgraph_get()
                bm = bmesh.new()
                bm.from_object(obj, depsgraph)
                bm.verts.ensure_lookup_table()

                options = [
                    bm.verts.layers.float_color,
                    bm.verts.layers.float_vector,
                    bm.verts.layers.float,
                ]

                for option in options:
                    for attribute in option:
                        if attribute.name[0] == ".":
                            continue
                        choice = context.scene.attribute_choices.add()
                        choice.attribute = attribute.name
                        choice.name = attribute.name
                        print(choice.attribute)

                bm.free()


class AttributeExporterCollection(bpy.types.PropertyGroup):
    pointer: bpy.props.PointerProperty(
        name="Collection", type=bpy.types.Collection
    )  # type: ignore



class AttributeExporterObject(bpy.types.PropertyGroup):
    object: bpy.props.PointerProperty(
        name="Object", type=bpy.types.Object
    )  # type: ignore


class AttributeExporterTarget(bpy.types.PropertyGroup):
    channel: bpy.props.EnumProperty(
        name="Target Channel",
        items=[
            ("-1", "Color", "Vertex Colors"),
            ("1", "UV1", "UV Channel"),
            ("2", "UV2", "UV Channel"),
            ("3", "UV3", "UV Channel"),
        ],
        default="1",
    )  # type: ignore
    component: bpy.props.EnumProperty(
        name="Target Component",
        items=[
            ("0", "X", "Component"),
            ("1", "Y", "Component"),
            ("2", "Z", "Component"),
            ("3", "W", "Component"),
        ],
        default="1",
    )  # type: ignore


class AttributeExporterAttribute(bpy.types.PropertyGroup):
    attribute: bpy.props.StringProperty(name="Attribute")  # type: ignore


# can't choose from a collection of strings, so we have to choose
# from a collection of AttributeExporterAttribute -- so we need
# AttributeExporterAttributeSelection to hold a single #AttributeExporterAttribute.
class AttributeExporterAttributeSelection(bpy.types.PropertyGroup):
    selection: bpy.props.PointerProperty(
        name="Attribute", type=AttributeExporterAttribute
    )  # type: ignore


class AttributeExporterEntry(bpy.types.PropertyGroup):
    label: bpy.props.StringProperty(name="Label")  # type: ignore
    collections: bpy.props.CollectionProperty(
        name="Collections", type=AttributeExporterCollection
    )  # type: ignore
    collections_index: bpy.props.IntProperty()  # type: ignore
    objects: bpy.props.CollectionProperty(
        name="Objects", type=AttributeExporterObject
    )  # type: ignore
    objects_index: bpy.props.IntProperty()  # type: ignore
    attributes: bpy.props.CollectionProperty(
        name="Attributes", type=AttributeExporterAttributeSelection
    )  # type: ignore
    attributes_index: bpy.props.IntProperty()  # type: ignore

    def get_objects(self) -> List[bpy.types.Object]:
        result = set()

        for obj in self.objects:
            if obj.object.visible_get():
                result.add(obj.object)

        for collection in self.collections:
            for obj in collection.pointer.all_objects:
                if obj.visible_get():
                    result.add(obj)

        return list(filter(lambda x: x.type == 'MESH', result))

class AttributeExporterPackage(bpy.types.PropertyGroup):
    label: bpy.props.StringProperty(name="Label")  # type: ignore
    path: bpy.props.StringProperty(name="Path", subtype="FILE_PATH", default="//")  # type: ignore
    entries: bpy.props.CollectionProperty(type=AttributeExporterEntry)  # type: ignore
    entries_index: bpy.props.IntProperty(update=refresh_attribute_choices)  # type: ignore
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
    default_vertex_storage : bpy.props.EnumProperty(
        name="Vertex Storage",
        description="How vertex data gets stored, by default",
        items=[
            ("MODIFIER", "Modifier", "Non-destructively set UVs with a modifier"),
            ("BAKED", "Baked", "Destructively set UVs. Necessary if shape keys need to be preserved.")
        ]
    ) # type: ignore


scene_props = {}

scene_props["attribute_exporter_packages"] = bpy.props.CollectionProperty(
    name="Packages", description="A list of packages", type=AttributeExporterPackage
)

scene_props["attribute_exporter_packages_index"] = bpy.props.IntProperty(
    name="Objects index",
    description="Object list index",
    update=refresh_attribute_choices,
)

scene_props["attribute_choices"] = bpy.props.CollectionProperty(
    name="Attribute Choices", type=AttributeExporterAttribute
)


class UVToggledGeonodeTree(bpy.types.PropertyGroup):
    tree: bpy.props.PointerProperty(name="Node Tree", type=bpy.types.GeometryNodeTree)  # type: ignore


scene_props["toggled_geonode_trees"] = bpy.props.CollectionProperty(
    name="Toggle Geonode Trees", type=UVToggledGeonodeTree
)

scene_props["toggled_geonode_trees_index"] = bpy.props.IntProperty(
    name="Toggle Geonode Tree Index"
)


def register():
    for id, prop in scene_props.items():
        setattr(bpy.types.Scene, id, prop)


def unregister():
    for id, prop in scene_props.items():
        delattr(bpy.types.Scene, id)
