import bpy
from .functions import (
    readWidgets,
    getViewLayerCollection,
    recurLayerCollection,
)
from .bl_class_registry import BlClassRegistry
from .menus import BONEWIDGET_MT_bw_specials



class VIEW3D_PT_bonewidget_panel:
    """BoneWidget Addon UI"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rigging"
    bl_label = "Bone Widget"

class VIEW3D_PT_bw_panel_main(VIEW3D_PT_bonewidget_panel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_bw_panel_main'
    bl_label = "Bone Widget"


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

        if bpy.context.mode == 'POSE':
            layout.operator("bonewidget.add_as_widget",
                            text="Use Selected Object",
                            icon='RESTRICT_SELECT_OFF')

        # if the bw collection exists, show the visibility toggle
        bw_collection_name = context.preferences.addons[__package__].preferences.bonewidget_collection_name
        bw_collection = recurLayerCollection(bpy.context.view_layer.layer_collection, bw_collection_name)

        if bw_collection is not None:
            if bw_collection.hide_viewport:
                icon = "HIDE_ON"
                text = "Show Collection"
            else:
                icon = "HIDE_OFF"
                text = "Hide Collection"
            row = layout.row()
            row.separator()
            row = layout.row()
            row.operator("bonewidget.toggle_collection_visibilty",
                         icon=icon, text=text)

class VIEW3D_PT_bw_panel_settings(VIEW3D_PT_bonewidget_panel, bpy.types.Panel):
    bl_parent_id = "VIEW3D_PT_bw_panel_main"
    bl_label = "Settings"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        scene = context.scene

        layout = self.layout
        col = layout.column()
        ### START TOOL SETTINGS UI BOX ###
        box_settings = col.row()
        col_box_settings = box_settings.column(align = True)

        row = col_box_settings.row(align = True)
        #row.prop(scene, "space_switcher_use_scene_frame_range", text = "Use Scene Frames Range", icon = "SCENE_DATA")

        row = col_box_settings.row(align = True)
        split_frames = col_box_settings.split()

        col_fr_start = split_frames.column()
        row = col_fr_start.row()
        row.label(text="Frame Start")
        row = col_fr_start.row()
        #row.prop(scene, "space_switcher_frame_start", text = "")

        col_fr_end = split_frames.column()
        row = col_fr_end.row()
        row.label(text="Frame End")
        row = col_fr_end.row()
        #row.prop(scene, "space_switcher_frame_end", text = "")

        if scene.space_switcher_use_scene_frame_range:
            col_fr_start.enabled = False
            col_fr_end.enabled = False

classes = (
    VIEW3D_PT_bw_panel_main,
    VIEW3D_PT_bw_panel_settings,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
