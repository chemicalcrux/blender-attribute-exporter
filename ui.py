import bpy

from . import props


def thing_exists(context, getter):
    return getter(context) is not None


def get_current_package(context):
    index = context.scene.uv_exporter_packages_index

    try:
        package = context.scene.uv_exporter_packages[index]
        return package
    except:
        return None


def get_current_entry(context):
    package = get_current_package(context)

    try:
        index = package.entries_index
        entry = package.entries[index]
        return entry
    except:
        return None


def get_current_object(context):
    entry = get_current_entry(context)

    try:
        index = entry.objects_index
        object = entry.objects[index]
        return object
    except:
        return None


def get_current_attribute(context):
    entry = get_current_entry(context)

    try:
        index = entry.attributes_index
        attribute = entry.attributes[index]
        return attribute
    except:
        return None


def remove_from_list(lst, index):
    lst.remove(index)

    index = max(0, index - 1)
    index = min(index, len(lst) - 1)

    return index


class UVRootPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_UV_root_panel"
    bl_label = "UV Exporter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UV Exporter"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Hello!!!")
        box.operator("uv.export_all")


class UVScenePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_UV_scene_panel"
    bl_parent_id = "OBJECT_PT_UV_root_panel"
    bl_label = "Packages"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UV Exporter"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.template_list(
            "UV_UL_PackageList",
            "Packages",
            context.scene,
            "uv_exporter_packages",
            context.scene,
            "uv_exporter_packages_index",
        )

        row = box.row()

        row.operator("uv.package_list_add", text="+")
        row.operator("uv.package_list_delete", text="-")


class UVPackagePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_UV_package_panel"
    bl_parent_id = "OBJECT_PT_UV_scene_panel"
    bl_label = "Package"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UV Exporter"
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return thing_exists(context, get_current_package)

    def draw(self, context):
        package = get_current_package(context)
        layout = self.layout
        box = layout.box()

        props = box.operator("uv.export")

        box.prop(package, "label")

        box.prop(package, "path")

        box.template_list(
            "UV_UL_EntryList",
            "Entries",
            package,
            "entries",
            package,
            "entries_index",
        )
        row = box.row()

        row.operator("uv.entry_list_add", text="+")
        row.operator("uv.entry_list_delete", text="-")

        row = box.row()

        row.prop(package, "source_uv")


class UVEntryPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_UV_entry_panel"
    bl_parent_id = "OBJECT_PT_UV_root_panel"
    bl_label = "Entry"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UV Exporter"
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return thing_exists(context, get_current_entry)

    def draw(self, context):
        entry = get_current_entry(context)
        layout = self.layout
        box = layout.box()

        box.prop(entry, "label")


class UVObjectsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_UV_objects_panel"
    bl_parent_id = "OBJECT_PT_UV_root_panel"
    bl_label = "Objects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UV Exporter"
    bl_order = 3

    @classmethod
    def poll(cls, context):
        return thing_exists(context, get_current_entry)

    def draw(self, context):
        entry = get_current_entry(context)
        layout = self.layout
        box = layout.box()
        box.template_list(
            "UV_UL_ObjectList",
            "Objects",
            entry,
            "objects",
            entry,
            "objects_index",
        )

        row = box.row()

        row.operator("uv.object_list_add", text="+")
        row.operator("uv.object_list_delete", text="-")


class UVAttributesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_UV_attributes_panel"
    bl_parent_id = "OBJECT_PT_UV_root_panel"
    bl_label = "Attributes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UV Exporter"
    bl_order = 4

    @classmethod
    def poll(cls, context):
        return thing_exists(context, get_current_entry)

    def draw(self, context):
        entry = get_current_entry(context)
        layout = self.layout
        box = layout.box()

        box.operator("uv.refresh")

        box.template_list(
            "UV_UL_AttributeList",
            "Attributes",
            entry,
            "attributes",
            entry,
            "attributes_index",
        )

        row = box.row()

        row.operator("uv.attribute_list_add", text="+")
        row.operator("uv.attribute_list_delete", text="-")


class UVAttributePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_UV_attribute_panel"
    bl_parent_id = "OBJECT_PT_UV_attributes_panel"
    bl_label = "Attribute"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UV Exporter"
    bl_order = 4

    @classmethod
    def poll(cls, context):
        return False
        # return thing_exists(context, get_current_attribute)

    def draw(self, context):
        attribute = get_current_attribute(context)
        layout = self.layout
        box = layout.box()

        box.prop(attribute, "attribute", text="")


class UV_UL_PackageList(bpy.types.UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
    ):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row()
            row.label(text=item.label if item.label else "Package...")
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon="OBJECT_DATAMODE")


class UV_PackageList_Add(bpy.types.Operator):
    bl_idname = "uv.package_list_add"
    bl_label = "Add view"

    def execute(self, context: bpy.types.Context):
        context.scene.uv_exporter_packages.add()
        return {"FINISHED"}


class UV_PackageList_Delete(bpy.types.Operator):
    bl_idname = "uv.package_list_delete"
    bl_label = "Delete view"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return thing_exists(context, get_current_package)

    def execute(self, context: bpy.types.Context):
        lst = context.scene.uv_exporter_packages
        index = context.scene.uv_exporter_packages_index

        context.scene.uv_exporter_packages_index = remove_from_list(lst, index)

        return {"FINISHED"}


class UV_UL_EntryList(bpy.types.UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
    ):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row()
            row.label(text=item.label if item.label else "Unnamed Entry")
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon="OBJECT_DATAMODE")


class UV_EntryList_Add(bpy.types.Operator):
    bl_idname = "uv.entry_list_add"
    bl_label = "Add entry"

    def execute(self, context: bpy.types.Context):
        get_current_package(context).entries.add()
        return {"FINISHED"}


class UV_EntryList_Delete(bpy.types.Operator):
    bl_idname = "uv.entry_list_delete"
    bl_label = "Remove entry"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return thing_exists(context, get_current_entry)

    def execute(self, context: bpy.types.Context):
        package = get_current_package(context)
        lst = package.entries
        index = package.entries_index

        package.entries_index = remove_from_list(lst, index)

        return {"FINISHED"}


class UV_UL_ObjectList(bpy.types.UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
    ):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row()
            row.prop(item, "object")
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon="OBJECT_DATAMODE")


class UV_ObjectList_Add(bpy.types.Operator):
    bl_idname = "uv.object_list_add"
    bl_label = "Add view"

    def execute(self, context: bpy.types.Context):
        entry = get_current_entry(context)
        entry.objects.add()
        return {"FINISHED"}


class UV_ObjectList_Delete(bpy.types.Operator):
    bl_idname = "uv.object_list_delete"
    bl_label = "Delete view"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return thing_exists(context, get_current_object)

    def execute(self, context: bpy.types.Context):
        entry = get_current_entry(context)
        lst = entry.objects
        index = entry.objects_index

        entry.objects_index = remove_from_list(lst, index)
        return {"FINISHED"}


class UV_UL_AttributeList(bpy.types.UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
    ):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row()
            row.prop_search(
                item.selection, "attribute", context.scene, "attribute_choices"
            )
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon="OBJECT_DATAMODE")


class UV_AttributeList_Add(bpy.types.Operator):
    bl_idname = "uv.attribute_list_add"
    bl_label = "Add view"

    def execute(self, context: bpy.types.Context):
        entry = get_current_entry(context)
        entry.attributes.add()
        return {"FINISHED"}


class UV_AttributeList_Delete(bpy.types.Operator):
    bl_idname = "uv.attribute_list_delete"
    bl_label = "Delete view"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return thing_exists(context, get_current_attribute)

    def execute(self, context: bpy.types.Context):
        entry = get_current_entry(context)
        lst = entry.attributes
        index = entry.attributes_index

        entry.item_index = remove_from_list(lst, index)
        return {"FINISHED"}


class UVGeonodePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_UV_geonode_panel"
    bl_label = "Geonode Toggles"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "UV Exporter"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        box = layout.box()

        box.template_list(
            "UV_UL_GeonodeList",
            "GeoNode Trees",
            context.scene,
            "toggled_geonode_trees",
            context.scene,
            "toggled_geonode_trees_index",
        )

        row = box.row()

        row.operator("uv.geonode_list_add", text="+")
        row.operator("uv.geonode_list_delete", text="-")


class UV_UL_GeonodeList(bpy.types.UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
    ):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row()
            row.prop_search(item, "tree", bpy.data, "node_groups")
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon="OBJECT_DATAMODE")


class UV_UL_GeonodeList_Add(bpy.types.Operator):
    bl_idname = "uv.geonode_list_add"
    bl_label = "Add tree"

    def execute(self, context: bpy.types.Context):
        context.scene.toggled_geonode_trees.add()
        return {"FINISHED"}


class UV_UL_GeonodeList_Delete(bpy.types.Operator):
    bl_idname = "uv.geonode_list_delete"
    bl_label = "Delete tree"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return len(context.scene.toggled_geonode_trees) > 0

    def execute(self, context: bpy.types.Context):
        lst = context.scene.toggled_geonode_trees
        index = context.scene.toggled_geonode_trees_index

        context.scene.toggled_geonode_trees_index = remove_from_list(lst, index)
        return {"FINISHED"}