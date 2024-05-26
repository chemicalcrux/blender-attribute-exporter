import bpy
import os

LIBRARY_NAME = "attribute-exporter-library.blend"
BLEND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attribute-exporter-library.blend")

def get_library():
    return bpy.data.libraries[LIBRARY_NAME]

def library_exists():
    return LIBRARY_NAME in bpy.data.libraries

def get_vertex_node_tree():
    library = get_library()
    return bpy.data.node_groups["Store Vertex ID", get_library().filepath]