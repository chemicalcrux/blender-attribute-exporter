from typing import List

import bpy


class EnsureGeonodes:
    """
    Geometry Node modifiers must be shown so that they show up in the
    bmesh data. However, exporting a model with any of these modifiers
    enabled causes shape keys to be lost.

    This context manager is used to enable all relevant modifiers before
    doing something, and to then disable them again afterwards.
    """

    objects: List[bpy.types.Object]
    context: bpy.types.Context

    def __init__(self, context: bpy.types.Context, objects: List[bpy.types.Object]):
        self.objects = []
        self.context = context

        for obj in objects:
            self.objects.append(obj)

    def __enter__(self):
        self.set_geonodes(True)
        self.context.view_layer.update()

    def __exit__(self, *args):
        self.set_geonodes(False)
        self.context.view_layer.update()

    def set_geonodes(self, state: bool):
        for obj in self.objects:
            for modifier in obj.modifiers:
                for tree in self.context.scene.toggled_geonode_trees:
                    if modifier.type == "NODES" and modifier.node_group == tree.tree:
                        modifier.show_render = state
                        modifier.show_viewport = state
