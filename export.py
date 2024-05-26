import struct
import os.path
from typing import Dict, Iterator, List, Tuple

import bmesh
import bpy
from mathutils import Vector

from . import props, library
from .context_managers import EnsureGeonodes

FORMAT_VERSION = 2


class Step:
    obj: bpy.types.Object
    source_uv: Tuple[int, int]
    vertex_storage: str
    attributes: List[str]

    def __init__(self, obj: bpy.types.Object, source_uv: Tuple[int, int], vertex_storage: str):
        self.obj = obj
        self.source_uv = source_uv
        self.vertex_storage = vertex_storage
        self.attributes = []


class Plan:
    steps: Dict[bpy.types.Object, Step]

    def __init__(self) -> None:
        self.steps = {}

    def register(self, obj: bpy.types.Object, source: Tuple[int, int], vertex_storage: str):
        if obj not in self.steps:
            self.steps[obj] = Step(obj, source, vertex_storage)

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


def perform_export(
    context: bpy.types.Context, package: props.UVExporterPackage
) -> None:
    plan = Plan()

    for entry in package.entries:
        for obj in entry.get_objects():
            plan.register(obj, (int(package.source_uv), 0), package.default_vertex_storage)
            for item in entry.attributes:
                plan.add(obj, item.selection.attribute)

    plan.validate()

    for step in plan.get_steps():
        print(step)

    output = b""

    output += struct.pack("<i", FORMAT_VERSION)
    output += struct.pack("<i", plan.get_object_count())

    with EnsureGeonodes(context, [step.obj for step in plan.get_steps()]):
        for step in plan.get_steps():
            output += write_object(step)
    
    filepath = bpy.path.abspath(package.path)
    filepath = os.path.join(filepath, package.label + ".attrdata")

    with open(
        filepath, "wb"
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

    while len(obj.data.uv_layers) <= source_uv_layer:
        print("Adding a UV map to " + obj.name)
        obj.data.uv_layers.new()

    if step.vertex_storage == 'MODIFIER':
        node_tree = library.get_vertex_node_tree()
        found = False

        for modifier in obj.modifiers:
            if modifier.type == "NODES" and modifier.node_group == node_tree:
                found = True
                break

        if not found: 
            print("Attaching a modifier to " + obj.name)
            modifier = obj.modifiers.new("Vertex IDs", 'NODES')
            modifier.node_group = library.get_vertex_node_tree()

        for layer in obj.data.uv_layers:
            if layer.name == "Vertex ID":
                layer.name = "UV Map"
                print("Renamed an old UV layer!")

        obj.data.uv_layers[source_uv_layer].name = "Vertex ID"


    for attribute in step.attributes:
        output += write_attrs(obj, attribute)

    if step.vertex_storage == 'BAKED':
        print("Baking vertex indices")

        for idx, loop in enumerate(obj.data.loops):
            obj.data.uv_layers[source_uv_layer].data[idx].uv = Vector((loop.vertex_index, 0))

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
        raise ValueError(f"Missing attribute: {obj.name} does not have {attribute}")

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
