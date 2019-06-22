import bpy
from .functions import readWidgets
from bpy.types import Menu


class BONEWIDGET_PT_posemode_panel(bpy.types.Panel):
    bl_label = "Bone Widget"
    bl_category = "RIG Tools"
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


class BONEWIDGET_MT_bw_specials(Menu):
    bl_label = "Bone Widget Specials"

    def draw(self, context):
        layout = self.layout
        layout.operator("bonewidget.symmetrize_shape", icon='MOD_MIRROR')
        layout.operator("bonewidget.match_bone_transforms", icon='GROUP_BONE')
        layout.operator("bonewidget.add_widgets", icon="ADD", text="Add Widgets")
        layout.operator("bonewidget.remove_widgets", icon="REMOVE", text="Remove Widgets")


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
