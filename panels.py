import bpy
from .functions import (
    readWidgets,
    getViewLayerCollection,
)
from bpy.types import Menu


class BONEWIDGET_PT_posemode_panel(bpy.types.Panel):
    bl_label = "Bone Widget"
    bl_category = "Rig Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_idname = 'VIEW3D_PT_bw_posemode_panel'

    items = []
    for key, value in readWidgets().items():
        items.append(key)

    itemsSort = []
    for key in sorted(items):
        itemsSort.append((key, key, ""))

    bpy.types.Scene.widget_list = bpy.props.EnumProperty(
        name="Shape", items=itemsSort, description="Shape")

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)

        if len(bpy.types.Scene.widget_list[1]['items']) < 6:
            row.prop(context.scene, "widget_list", expand=True)
        else:
            row.prop(context.scene, "widget_list", expand=False, text="")

        row = layout.row(align=True)
        row.menu("BONEWIDGET_MT_bw_specials", icon='DOWNARROW_HLT', text="")
        row.operator("bonewidget.create_widget", icon="OBJECT_DATAMODE")

        if bpy.context.mode == "POSE":
            row.operator("bonewidget.edit_widget", icon="OUTLINER_DATA_MESH")
        else:
            row.operator("bonewidget.return_to_armature", icon="LOOP_BACK", text='To bone')

        collection = getViewLayerCollection(context)
        if collection.hide_viewport:
            icon = "HIDE_ON"
            text = "Unhide Collection"
        else:
            icon = "HIDE_OFF"
            text = "Hide Collection"
        row = layout.row()
        row.operator("bonewidget.toggle_collection_visibilty",
                     icon=icon, text=text)

        layout = self.layout
        layout.operator("bonewidget.symmetrize_shape", icon='MOD_MIRROR', text="Symmetrize Shape")
        layout.operator("bonewidget.match_bone_transforms",
                        icon='GROUP_BONE', text="Match Bone Transforms")
        layout.operator("bonewidget.delete_unused_widgets",
                        icon='GROUP_BONE', text="Delete Unused Widgets")
        layout.operator("bonewidget.clear_widgets",
                        icon='GROUP_BONE', text="Clear Bone Widgets")


class BONEWIDGET_MT_bw_specials(Menu):
    bl_label = "Bone Widget Specials"

    def draw(self, context):
        layout = self.layout
        layout.operator("bonewidget.add_widgets", icon="ADD", text="Add Widget to library")
        layout.operator("bonewidget.remove_widgets", icon="REMOVE",
                        text="Remove Widget from library")


classes = (
    BONEWIDGET_MT_bw_specials,
    BONEWIDGET_PT_posemode_panel,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
