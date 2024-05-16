import bpy
import struct
from mathutils import Vector
import bmesh
import blender_uv_exporter.ui
import blender_uv_exporter.props


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

    return output


def write_attrs(obj, attribute_name, target_uv_layer):
    output = b""

    depsgraph = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()

    bm.from_object(obj, depsgraph)

    bm.verts.ensure_lookup_table()

    layer = bm.verts.layers.float_color[attribute_name]

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

    for idx, loop in enumerate(obj.data.loops):
        (punned,) = struct.unpack("<f", struct.pack("<i", loop.vertex_index))
        obj.data.uv_layers[source_uv_layer].data[idx].uv = Vector((punned, 0))

    for item in colors:
        output += struct.pack("<f", item)

    return output

def perform_export(package):
    plan = []

    for entry in package.entries:
        for obj in entry.objects:
            step = {}
            step["object"] = obj.object
            step["attributes"] = []
            step["targets"] = []

            for item in entry.attributes:
                step["attributes"].append(item.attribute)
                step["targets"].append(int(item.target_channel))

            print(step)

            plan.append(step)

    output = b""

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
        perform_export(package)

        return {"FINISHED"}

class UV_Export_All(bpy.types.Operator):
    bl_idname = "uv.export_all"
    bl_label = "Export All Data"

    def execute(self, context: bpy.types.Context):
        for package in context.scene.uv_exporter_packages:
            perform_export(package)

        return {"FINISHED"}

plan = [
    {
        "object": "One",
        "attributes": ["Pose Space", "Curve Direction"],
        "targets": [2, 1],
    }
]
