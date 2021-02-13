import bpy
from .functions import (
    readWidgets,
    getViewLayerCollection,
)
from .bl_class_registry import BlClassRegistry
from .menus import BONEWIDGET_MT_bw_specials


@BlClassRegistry()
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
        items=itemsSort, name="Shape", description="Shape")

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

        layout = self.layout
        layout.separator()
        layout.operator("bonewidget.symmetrize_shape", icon='MOD_MIRROR', text="Symmetrize Shape")
        layout.operator("bonewidget.match_bone_transforms",
                        icon='GROUP_BONE', text="Match Bone Transforms")
        layout.operator("bonewidget.resync_widget_names",
                        icon='FILE_REFRESH', text="Resync Widget Names")
        layout.separator()
        layout.operator("bonewidget.clear_widgets",
                        icon='X', text="Clear Bone Widget")
        layout.operator("bonewidget.delete_unused_widgets",
                        icon='TRASH', text="Delete Unused Widgets")

        import os
        path = os.path.join(os.path.expanduser("~"), "Blender Addons Data", "bonewidget", "temp.txt")
        if bpy.context.mode.title() == 'Pose':
            layout.operator("bonewidget.select_object",
                            text="Select Object as widget shape",
                            icon='RESTRICT_SELECT_OFF')
        elif bpy.context.mode.title() == 'Object' and os.path.exists(path):
            layout.operator("bonewidget.confirm_widget",
                            text="Confirm selected Object as widget shape",
                            icon='CHECKMARK')

        try:
            collection = getViewLayerCollection(context)
        except:
            collection = None

        if collection is not None:
            if collection.hide_viewport:
                icon = "HIDE_ON"
                text = "Unhide Collection"
            else:
                icon = "HIDE_OFF"
                text = "Hide Collection"
            row = layout.row()
            row.separator()
            row = layout.row()
            row.operator("bonewidget.toggle_collection_visibilty",
                         icon=icon, text=text)
