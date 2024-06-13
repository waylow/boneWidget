import bpy
import bpy.utils.previews
from .functions import (
    readWidgets,
    getViewLayerCollection,
    recurLayerCollection,
    preview_collections,
    generate_previews,
    preview_update,
)

from .menus import BONEWIDGET_MT_bw_specials


class BONEWIDGET_PT_bw_panel:
    """BoneWidget Addon UI"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rigging"
    bl_label = "Bone Widget"

class BONEWIDGET_PT_bw_panel_main(BONEWIDGET_PT_bw_panel, bpy.types.Panel):
    bl_idname = 'BONEWIDGET_PT_bw_panel_main'
    bl_label = "Bone Widget"


    bpy.types.WindowManager.toggle_preview = bpy.props.BoolProperty(
        name="Display Previews",
        default=True,
        description="Show thumbnail previews"
    )

    itemsSort = []
    for key, value in sorted(readWidgets().items()):
        itemsSort.append((key, key, ""))

    bpy.types.Scene.widget_list = bpy.props.EnumProperty(
        items=itemsSort, name="Shape", description="Shape")

    pcoll = bpy.utils.previews.new()
    pcoll.widget_list = ()
    preview_collections["widgets"] = pcoll

    bpy.types.WindowManager.widget_list = bpy.props.EnumProperty(
        items=generate_previews(), name="Shape", description="Shape", update=preview_update
    )

    def draw(self, context):
        layout = self.layout
        
        # preview toggle checkbox
        row = layout.row(align=True)
        row.prop(context.window_manager, "toggle_preview")
        
        # preview view
        if context.window_manager.toggle_preview:
            row = layout.row(align=True)
            row.template_icon_view(context.window_manager, "widget_list", show_labels=True)


        # dropdown list
        row = layout.row(align=True)
        row.prop(context.window_manager, "widget_list", expand=False, text="")

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
        if not context.preferences.addons[__package__].preferences.use_rigify_defaults:
            bw_collection_name = context.preferences.addons[__package__].preferences.bonewidget_collection_name
        else:
            bw_collection_name = 'WGTS_' + context.active_object.name
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

classes = (
    BONEWIDGET_PT_bw_panel_main,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    del bpy.types.WindowManager.widget_list

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
