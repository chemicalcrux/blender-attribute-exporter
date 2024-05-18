import bpy
import struct
from mathutils import Vector
import bmesh
from . import ui
from . import props
from typing import List, Dict, Tuple, NamedTuple, Iterator


class Step():
    obj: bpy.types.Object
    source_uv: Tuple[int, int]
    attributes: List[str]

    def __init__(self, obj: bpy.types.Object, source_uv: Tuple[int, int]):
        self.obj = obj
        self.source_uv = source_uv
        self.attributes = []


class Plan:
    steps: Dict[bpy.types.Object, Step]

    def __init__(self) -> None:
        self.steps = {}

    def register(self, obj: bpy.types.Object, source: Tuple[int, int]):
        if obj not in self.steps:
            self.steps[obj] = Step(obj, source)

    def add(self, obj: bpy.types.Object, attribute: str) -> None:
        self.steps[obj].attributes.append(attribute)

    def validate(self) -> None:
        for obj, step in self.steps.items():
            seen = set()

            for attribute in step.attributes:
                if attribute in seen:
                    raise ValueError(
                        f"Duplicate part: {obj.name} tries to export {attribute} more than once."
                    )
                seen.add(attribute)

    def get_steps(self) -> Iterator[Step]:
        for step in self.steps.values():
            yield step

    def get_object_count(self) -> int:
        return len(self.steps)


def perform_export(package: props.UVExporterPackage) -> None:
    plan = Plan()

    for entry in package.entries:
        for obj in entry.objects:
            plan.register(obj.object, (int(package.source_uv), 0))
            for item in entry.attributes:
                plan.add(obj.object, item.attribute)

    plan.validate()

    for step in plan.get_steps():
        print(step)

    output = b""

    output += struct.pack("<i", plan.get_object_count())

    for step in plan.get_steps():
        output += write_object(step)

    print(bpy.path.abspath(package.path) + "/" + package.label + ".uv")
    with open(
        bpy.path.abspath(package.path) + "/" + package.label + ".uv", "wb"
    ) as file:
        file.write(output)


def write_object(step: Step):
    output = b""
    
    obj = step.obj

    encoded_name = obj.name.encode("utf-8")
    padding = (4 - len(encoded_name)) % 4

    output += struct.pack("<i", len(encoded_name))
    output += encoded_name
    output += b"\x00" * padding

    source_uv_layer = step.source_uv[0]
    source_uv_dim = step.source_uv[1]

    output += struct.pack("<i", source_uv_layer)
    output += struct.pack("<i", source_uv_dim)
    output += struct.pack("<i", len(step.attributes))

    for attribute in step.attributes:
        output += write_attrs(obj, attribute)

    for idx, loop in enumerate(obj.data.loops):
        if idx % 1000 == 0:
            print(idx)
        (punned,) = struct.unpack("<f", struct.pack("<i", loop.vertex_index))
        obj.data.uv_layers[source_uv_layer].data[idx].uv = Vector((punned, 0))

    return output


def write_attrs(obj: bpy.types.Object, attribute: str) -> None:
    output = b""

    depsgraph = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()

    bm.from_object(obj, depsgraph)

    bm.verts.ensure_lookup_table()

    print("Attribute: " + attribute)

    if attribute in bm.verts.layers.float_color:
        layer = bm.verts.layers.float_color[attribute]
        dimensions = 4
    elif attribute in bm.verts.layers.float_vector:
        layer = bm.verts.layers.float_vector[attribute]
        dimensions = 3
    elif attribute in bm.verts.layers.float:
        layer = bm.verts.layers.float[attribute]
        dimensions = 1
    else:
        raise ValueError(
            f"Missing attribute: {obj.name} does not have {attribute}"
        )

    vertex_count = len(bm.verts)
    encoded_name = attribute.encode("utf-8")
    padding = (4 - len(encoded_name)) % 4

    output += struct.pack("<i", len(encoded_name))
    output += encoded_name
    output += b"\x00" * padding

    output += struct.pack("<i", vertex_count)
    output += struct.pack("<i", dimensions)

    colors = [0] * dimensions * vertex_count

    for item_index, item in enumerate(bm.verts):
        if dimensions == 1:
            colors[item_index] = item[layer]
        else:
            for dim, color in enumerate(item[layer]):
                index = item_index * dimensions + dim
                colors[index] = color

    bm.free()

    for item in colors:
        output += struct.pack("<f", item)

    return output


class UV_Export(bpy.types.Operator):
    bl_idname = "uv.export"
    bl_label = "Export Data"

    def execute(self, context: bpy.types.Context):
        package = ui.get_current_package(context)

        try:
            perform_export(package)
        except ValueError as e:
            self.report({"ERROR"}, str(e))

        return {"FINISHED"}


class UV_Export_All(bpy.types.Operator):
    bl_idname = "uv.export_all"
    bl_label = "Export All Data"

    def execute(self, context: bpy.types.Context):
        for package in context.scene.uv_exporter_packages:
            perform_export(package)

        return {"FINISHED"}
