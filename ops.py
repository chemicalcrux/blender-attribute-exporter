import bpy
import struct
from mathutils import Vector
import bmesh
import blender_uv_exporter.ui
import blender_uv_exporter.props
from typing import List, Dict, Tuple, NamedTuple, Iterator


def write_object(obj, attribute_names, target_uv_layers):
    output = b""

    encoded_name = obj.name.encode("utf-8")
    padding = (4 - len(encoded_name)) % 4

    output += struct.pack("<i", len(encoded_name))
    output += encoded_name
    output += b"\x00" * padding

    source_uv_layer = 1
    source_uv_dim = 0

    output += struct.pack("<i", source_uv_layer)
    output += struct.pack("<i", source_uv_dim)
    output += struct.pack("<i", len(attribute_names))

    for attr_name, target in zip(attribute_names, target_uv_layers):
        output += write_attrs(obj, attr_name, target)

    for idx, loop in enumerate(obj.data.loops):
        if idx % 1000 == 0:
            print(idx)
        (punned,) = struct.unpack("<f", struct.pack("<i", loop.vertex_index))
        obj.data.uv_layers[source_uv_layer].data[idx].uv = Vector((punned, 0))

    return output


def write_attrs(obj, attribute_name, target_uv_layer):
    output = b""

    depsgraph = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()

    bm.from_object(obj, depsgraph)

    bm.verts.ensure_lookup_table()

    try:
        layer = bm.verts.layers.float_color[attribute_name]
    except:
        raise ValueError(
            f"Missing attribute: {obj.name} does not have {attribute_name}"
        )

    source_uv_layer = 1
    source_uv_dim = 0
    dimensions = 4
    vertex_count = len(bm.verts)

    output += struct.pack("<i", target_uv_layer)
    output += struct.pack("<i", dimensions)
    output += struct.pack("<i", vertex_count)

    colors = [0] * 4 * vertex_count

    for item_index, item in enumerate(bm.verts):
        for dim, color in enumerate(item[layer]):
            index = item_index * 4 + dim
            colors[index] = color

    bm.free()

    for item in colors:
        output += struct.pack("<f", item)

    return output


class StepPart(NamedTuple):
    attribute: str
    source: Tuple[int, int]
    target: Tuple[int, int]


class Plan:
    steps: Dict[bpy.types.Object, List[StepPart]]

    def __init__(self) -> None:
        self.steps = {}

    def add(
        self, obj: bpy.types.Object, attribute: str, source: Tuple[int, int], target: Tuple[int, int]
    ) -> None:
        if obj not in self.steps:
            self.steps[obj] = []

        self.steps[obj].append(
            StepPart(attribute=attribute, source=source, target=target)
        )

    def validate(self) -> None:
        for obj, parts in self.steps.items():
            seen = set()

            for part in parts:
                target = (part.channel, part.component)
                if target in seen:
                    raise ValueError(
                        f"Duplicate target: {obj.name} targets UV{part.channel}.{part.component} more than once"
                    )
                seen.add(target)
    
    def get_steps(self) -> Iterator[Tuple[bpy.types.Object, List[StepPart]]]:
        for obj, parts in self.steps.items():
            yield (obj, parts)


def perform_export(package):
    plan = Plan()

    for entry in package.entries:
        for obj in entry.objects:
            for item in entry.attributes:
                if (item.red_target_used):
                    plan.add(obj, item.attribute, int(item.red_target.channel), int(item.red_target.component))
                if (item.green_target_used):
                    plan.add(obj, item.attribute, int(item.green_target.channel), int(item.green_target.component))
                if (item.blue_target_used):
                    plan.add(obj, item.attribute, int(item.blue_target.channel), int(item.blue_target.component))
                if (item.alpha_target_used):
                    plan.add(obj, item.attribute, int(item.alpha_target.channel), int(item.alpha_target.component))

    plan.validate()

    for step in plan.get_steps():
        print(step)

    output = b""

    output += struct.pack("<i", 1)
    output += struct.pack("<i", 1)
    output += struct.pack("<i", 1)
    output += struct.pack("<i", 1)

    output += struct.pack("<i", len(plan))

    for item in plan:
        output += write_object(item["object"], item["attributes"], item["targets"])

    print(bpy.path.abspath(package.path) + "/" + package.label + ".uv")
    with open(
        bpy.path.abspath(package.path) + "/" + package.label + ".uv", "wb"
    ) as file:
        file.write(output)


class UV_Export(bpy.types.Operator):
    bl_idname = "uv.export"
    bl_label = "Export Data"

    def execute(self, context: bpy.types.Context):
        package = blender_uv_exporter.ui.get_current_package(context)

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
