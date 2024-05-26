import bpy

from . import props, library


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


def get_current_collection(context):
    entry = get_current_entry(context)

    try:
        return entry.collections[entry.collections_index]
    except:
        return None


def get_current_object(context):
    entry = get_current_entry(context)

    try:
        return entry.objects[entry.objects_index]
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

        if not library.library_exists():
            layout.operator("uv.link_library")
        else:
            layout.label(text=f"Packages: {len(context.scene.uv_exporter_packages)}")
            layout.operator("uv.export_all")


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

        layout.template_list(
            "UV_UL_PackageList",
            "Packages",
            context.scene,
            "uv_exporter_packages",
            context.scene,
            "uv_exporter_packages_index",
        )

        row = layout.row()

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

        props = layout.operator("uv.export")

        layout.prop(package, "label")

        layout.prop(package, "path")

        layout.template_list(
            "UV_UL_EntryList",
            "Entries",
            package,
            "entries",
            package,
            "entries_index",
        )
        row = layout.row()

        row.operator("uv.entry_list_add", text="+")
        row.operator("uv.entry_list_delete", text="-")

        layout.prop(package, "source_uv")
        layout.prop(package, "default_vertex_storage")


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
        layout.prop(entry, "label")


class UVObjectsPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_UV_objects_panel"
    bl_parent_id = "OBJECT_PT_UV_entry_panel"
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
        
        row = layout.row()
        split = row.split(factor=0.5)

        box = split.box()
        box.label(text="Collections")
        box.template_list(
            "UV_UL_CollectionList",
            "Collections",
            entry,
            "collections",
            entry,
            "collections_index",
        )

        inner_row = box.row()

        inner_row.operator("uv.collection_list_add", text="+")

        box = split.box()
        box.label(text="Objects")
        box.template_list(
            "UV_UL_ObjectList",
            "Objects",
            entry,
            "objects",
            entry,
            "objects_index",
        )

        inner_row = box.row()

        inner_row.operator("uv.object_list_add", text="+")


class UVAttributesPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_UV_attributes_panel"
    bl_parent_id = "OBJECT_PT_UV_entry_panel"
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

        layout.operator("uv.refresh")

        layout.template_list(
            "UV_UL_AttributeList",
            "Attributes",
            entry,
            "attributes",
            entry,
            "attributes_index",
        )

        row = layout.row()

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


class UV_UL_CollectionList(bpy.types.UIList):
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
            split = row.split(factor=0.75)
            split.prop(item, "pointer", text='')
            op = split.operator("uv.collection_list_delete", text="-")
            op.index = index
        elif self.layout_type in {"GRID"}:
            
            layout.alignment = "CENTER"
            layout.label(text="", icon="OBJECT_DATAMODE")


class UV_CollectionList_Add(bpy.types.Operator):
    bl_idname = "uv.collection_list_add"
    bl_label = "Add view"

    def execute(self, context: bpy.types.Context):
        entry = get_current_entry(context)
        entry.collections.add()
        return {"FINISHED"}


class UV_CollectionList_Delete(bpy.types.Operator):
    bl_idname = "uv.collection_list_delete"
    bl_label = "Delete view"
    index: bpy.props.IntProperty() # type: ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return thing_exists(context, get_current_collection)

    def execute(self, context: bpy.types.Context):
        entry = get_current_entry(context)
        lst = entry.collections
        index = self.index

        entry.collections_index = remove_from_list(lst, index)
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
            split = row.split(factor=0.75)
            split.prop(item, "object", text='')
            op = split.operator("uv.object_list_delete", text="-")
            op.index = index
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
    index: bpy.props.IntProperty() # type: ignore

    @classmethod
    def poll(self, context: bpy.types.Context):
        return thing_exists(context, get_current_object)

    def execute(self, context: bpy.types.Context):
        entry = get_current_entry(context)
        lst = entry.objects
        index = self.index

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

        layout.template_list(
            "UV_UL_GeonodeList",
            "GeoNode Trees",
            context.scene,
            "toggled_geonode_trees",
            context.scene,
            "toggled_geonode_trees_index",
        )

        row = layout.row()

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