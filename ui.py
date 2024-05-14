import bpy

from blender_uv_exporter import props

class UVScenePanel(bpy.types.Panel):
    bl_idname="OBJECT_PT_UV_scene_panel"
    bl_label="UV Exporter"
    bl_space_type="VIEW_3D"
    bl_region_type="UI"
    bl_category="UV Exporter"

    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Hello!!!")
        box.operator("uv.export")
        box.prop
        box.template_list(
            "UV_UL_ObjectList",
            "Objects",
            context.scene,
            "uv_exporter_objects",
            context.scene,
            "uv_exporter_objects_index"
        )
        
        row = box.row()

        row.operator("uv.object_list_add", text="+")
        row.operator("uv.object_list_delete", text="-")

        if context.scene.uv_exporter_objects_index >= 0 and context.scene.uv_exporter_objects:
            index = context.scene.uv_exporter_objects_index
            obj = context.scene.uv_exporter_objects[index]

            box.template_list(
                "UV_UL_AttributeList",
                "Attributes",
                obj,
                "items",
                obj,
                "item_index"
            )

            row = box.row()
            
            row.operator("uv.attribute_list_add", text="+")
            row.operator("uv.attribute_list_delete", text="-")

class UV_UL_ObjectList(bpy.types.UIList):
    def draw_item(self, context, layout: bpy.types.UILayout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            box = layout.box()

            if item.object:
                label = item.object.name
            else:
                label = "Empty"

            box.label(text = label)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='', icon = 'OBJECT_DATAMODE')

class UV_ObjectList_Add(bpy.types.Operator):
    bl_idname = "uv.object_list_add"
    bl_label = "Add view"

    def execute(self, context: bpy.types.Context):
        context.scene.uv_exporter_objects.add()
        return {'FINISHED'}

class UV_ObjectList_Delete(bpy.types.Operator):
    bl_idname = "uv.object_list_delete"
    bl_label = "Delete view"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return context.scene.uv_exporter_objects

    def execute(self, context: bpy.types.Context):
        lst = context.scene.uv_exporter_objects
        index = context.scene.uv_exporter_objects_index

        lst.remove(index)

        index = max(0, index - 1)
        index = min(index, len(lst) - 1)

        context.scene.uv_exporter_objects_index = index
        return {'FINISHED'}

class UV_UL_AttributeList(bpy.types.UIList):
    def draw_item(self, context, layout: bpy.types.UILayout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            box = layout.box()

            row = box.row()
            row.prop_enum(item, "target_channel", "0")
            row.prop_enum(item, "target_channel", "1")
            row.prop_enum(item, "target_channel", "2")
            row.prop_enum(item, "target_channel", "3")

            row = box.row()

            row.prop(item, "attribute")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='', icon = 'OBJECT_DATAMODE')

class UV_AttributeList_Add(bpy.types.Operator):
    bl_idname = "uv.attribute_list_add"
    bl_label = "Add view"

    def execute(self, context: bpy.types.Context):
        obj = context.scene.uv_exporter_objects[context.scene.uv_exporter_objects_index]
        obj.items.add()
        return {'FINISHED'}

class UV_AttributeList_Delete(bpy.types.Operator):
    bl_idname = "uv.attribute_list_delete"
    bl_label = "Delete view"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return context.scene.uv_exporter_objects

    def execute(self, context: bpy.types.Context):
        obj = context.scene.uv_exporter_objects[context.scene.uv_exporter_objects_index]
        lst = obj.items
        index = obj.item_index

        lst.remove(index)

        index = max(0, index - 1)
        index = min(index, len(lst) - 1)

        obj.item_index = index
        return {'FINISHED'}
