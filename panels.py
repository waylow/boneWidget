import bpy
import bpy.utils.previews
from .functions import (
    recurLayerCollection,
    preview_collections,
    createPreviewCollection,
    get_preview_default,
    bone_color_items_short,
    updateBoneColor,
    updateEditBoneColor,
    live_update_toggle,
    getPreferences,
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


    createPreviewCollection()

    def draw(self, context):
        layout = self.layout
        
        # preview toggle checkbox
        row = layout.row(align=True)
        row.prop(context.window_manager, "toggle_preview")
        
        # preview view
        if context.window_manager.toggle_preview:
            row = layout.row(align=True)
            preview_panel_size = getPreferences(context).preview_panel_size
            preview_popup_size = getPreferences(context).preview_popup_size
            row.template_icon_view(context.window_manager, "widget_list", show_labels=True,
                                   scale=preview_panel_size, scale_popup=preview_popup_size)

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

        # BONE COLORS
        if bpy.app.version >= (4,2,0) and not (context.object.mode == "EDIT"
                                    and getPreferences(context).edit_bone_colors == False):
            layout.separator()
            row = layout.row(align=True)
            row.operator("bonewidget.set_bone_color", text="Set Bone Color", icon="BRUSHES_ALL")
            row.scale_x = 3.0
            row.template_icon_view(context.window_manager, "bone_widget_colors", show_labels=False, scale=1, scale_popup=1.8)
            if context.window_manager.bone_widget_colors == "CUSTOM":
                
                row = layout.row(align=True)
                if context.object.mode == 'POSE': # display pose bone colors
                    row.prop(context.scene, "colorset_normal", text="")
                    row.prop(context.scene, "colorset_select", text="")
                    row.prop(context.scene, "colorset_active", text="")
                elif context.object.mode == "EDIT": #edit bone colors
                    row.prop(context.scene, "edit_colorset_normal", text="")
                    row.prop(context.scene, "edit_colorset_select", text="")
                    row.prop(context.scene, "edit_colorset_active", text="")
                
                if context.object.mode in ['POSE', 'EDIT']:
                    row.separator(factor=0.5)
                    row.prop(context.scene, "live_update_toggle", text="", icon="UV_SYNC_SELECT")
                    row = layout.row(align=True)

                row.operator("bonewidget.copy_bone_color", text="Copy Bone Color", icon="COPYDOWN")
            row = layout.row(align=True)
            row.operator("bonewidget.clear_bone_color", text="Clear Bone Color", icon="PANEL_CLOSE")

        # if the bw collection exists, show the visibility toggle
        if not getPreferences(context).use_rigify_defaults: #rigify
            bw_collection_name = getPreferences(context).bonewidget_collection_name
        
        elif context.active_object: # active  object
            bw_collection_name = 'WGTS_' + context.active_object.name
        
        else: # this is needed because sometimes there is no active object
            bw_collection_name = None 
        
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
    bpy.types.WindowManager.toggle_preview = bpy.props.BoolProperty(
        name="Preview Panel",
        default=get_preview_default(),
        description="Show thumbnail previews"
    )

    bpy.types.WindowManager.bone_widget_colors = bpy.props.EnumProperty(
        name="Colors",
        description="Select a Bone Color",
        items=bone_color_items_short,
        default=1, # THEME01
    )

    bpy.types.Scene.colorset_normal = bpy.props.FloatVectorProperty(
        name="Normal",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for the surface of bones",
        update=updateBoneColor,
    )

    bpy.types.Scene.colorset_select = bpy.props.FloatVectorProperty(
        name="Select",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for selected bones",
        update=updateBoneColor,
    )

    bpy.types.Scene.colorset_active = bpy.props.FloatVectorProperty(
        name="Active",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for active bones",
        update=updateBoneColor,
    )

    bpy.types.Scene.edit_colorset_normal = bpy.props.FloatVectorProperty(
        name="Normal",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for the surface of edit bones",
        update=updateEditBoneColor,
    )

    bpy.types.Scene.edit_colorset_select = bpy.props.FloatVectorProperty(
        name="Select",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for selected edit bones",
        update=updateEditBoneColor,
    )

    bpy.types.Scene.edit_colorset_active = bpy.props.FloatVectorProperty(
        name="Active",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for active edit bones",
        update=updateEditBoneColor,
    )

    bpy.types.Scene.live_update_on = bpy.props.BoolProperty(
        name="Live Update",
        description="Live Update on or off",
        default=False,
    )

    bpy.types.Scene.live_update_toggle = bpy.props.BoolProperty(
        name="Live Update Toggle",
        description="Toggles Live Update on/off for custom colors",
        default=bpy.types.Scene.live_update_on.keywords['default'],
        update=live_update_toggle,
    )
    
    from bpy.utils import register_class
    for cls in classes:
        try:
            register_class(cls)
        except:
            pass


def unregister():
    del bpy.types.WindowManager.widget_list
    del bpy.types.WindowManager.toggle_preview
    del bpy.types.WindowManager.bone_widget_colors
    del bpy.types.Scene.colorset_normal
    del bpy.types.Scene.colorset_select
    del bpy.types.Scene.colorset_active
    del bpy.types.Scene.edit_colorset_normal
    del bpy.types.Scene.edit_colorset_select
    del bpy.types.Scene.edit_colorset_active
    del bpy.types.Scene.live_update_on
    del bpy.types.Scene.live_update_toggle

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    
    from bpy.utils import unregister_class
    for cls in classes:
        try:
            unregister_class(cls)
        except:
            pass
