import bpy
import bpy.utils.previews
from .props import PresetColorSetItem, CustomColorSet
from .functions import (
    recurLayerCollection,
    preview_collections,
    createPreviewCollection,
    get_preview_default,
    bone_color_items_short,
    live_update_toggle,
    loadColorPresets,
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

        # BONE COLORS
        if bpy.app.version >= (4,0,0):
            
            layout.separator()
            row = layout.row(align=True)
            row.operator("bonewidget.set_bone_color", text="Set Bone Color", icon="BRUSHES_ALL")
            row.scale_x = 3.0
            row.template_icon_view(context.scene, "bone_widget_colors", show_labels=False, scale=1, scale_popup=1.8)
            if context.scene.bone_widget_colors == "CUSTOM":

                custom_pose_color = context.scene.custom_pose_color_set
                custom_edit_color = context.scene.custom_edit_color_set
                
                row = layout.row(align=True)
                if context.object.mode == 'POSE': # display pose bone colors
                    row.prop(custom_pose_color, "normal", text="")
                    row.prop(custom_pose_color, "select", text="")
                    row.prop(custom_pose_color, "active", text="")
                elif context.object.mode == "EDIT" and getPreferences(context).edit_bone_colors: #edit bone colors
                    row.prop(custom_edit_color, "normal", text="")
                    row.prop(custom_edit_color, "select", text="")
                    row.prop(custom_edit_color, "active", text="")
                
                if context.object.mode == "POSE" or getPreferences(context).edit_bone_colors:
                    row.separator(factor=0.5)
                    row.prop(context.scene, "live_update_toggle", text="", icon="UV_SYNC_SELECT")
                    row = layout.row(align=True)

                    row.operator("bonewidget.copy_bone_color", text="Copy Bone Color", icon="COPYDOWN")
            row = layout.row(align=True)
            row.operator("bonewidget.clear_bone_color", text="Clear Bone Color", icon="PANEL_CLOSE")


class BONEWIDGET_PT_bw_custom_color_presets(BONEWIDGET_PT_bw_panel, bpy.types.Panel):
    bl_idname = "BONEWIDGET_PT_bw_custom_color_presets"
    bl_parent_id = "BONEWIDGET_PT_bw_panel_main"
    bl_label = "Custom Color Presets"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return bpy.app.version >= (4,0,0)
    
    def draw(self, context):
        layout = self.layout

        row = layout.row()
        btn_text = "Add From Theme" if "THEME" in context.scene.bone_widget_colors else "Add From Palette"
        row.operator("bonewidget.add_color_set_from", text=btn_text, icon="ADD")

        row = layout.row()
        row.template_list("BONEWIDGET_UL_colorset_items", "", context.window_manager, "custom_color_presets",
                          context.window_manager, "colorset_list_index")
        
        col = row.column(align=True)
        col.operator("bonewidget.add_default_custom_colorset", icon='ADD', text="")
        col.operator("bonewidget.remove_custom_item", icon='REMOVE', text="")
        col.separator()
        col.separator()
        colorset_locked = context.scene.lock_colorset_color_changes
        col.operator("bonewidget.lock_custom_colorset_changes", icon="LOCKED" if colorset_locked else "UNLOCKED", text="")

        if colorset_locked: # only allow refresh if list is locked
            col.separator()
            col.operator("bonewidget.reload_colorset_items", icon="FILE_REFRESH", text="")

        row = layout.row()
        row.operator("bonewidget.add_colorset_to_bone", text="Apply To Selected Bones")


class BONEWIDGET_UL_colorset_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        split = layout.split(factor=0.58) # set the size of each color set field
        split.prop(item, "name", text="", emboss=False)
        
        row = split.row(align=True)
        row.prop(item, "normal", text="")
        row.prop(item, "select", text="")
        row.prop(item, "active", text="")


classes = (
    BONEWIDGET_PT_bw_panel_main,
    BONEWIDGET_PT_bw_custom_color_presets,
    BONEWIDGET_UL_colorset_items,
)


def register():
    bpy.types.WindowManager.toggle_preview = bpy.props.BoolProperty(
        name="Preview Panel",
        default=get_preview_default(),
        description="Show thumbnail previews"
    )

    bpy.types.Scene.bone_widget_colors = bpy.props.EnumProperty(
        name="Colors",
        description="Select a Bone Color",
        items=bone_color_items_short,
        default=1, # THEME01
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

    bpy.utils.register_class(PresetColorSetItem)
    bpy.utils.register_class(CustomColorSet)
    bpy.types.WindowManager.custom_color_presets = bpy.props.CollectionProperty(type=PresetColorSetItem)
    bpy.types.Scene.custom_pose_color_set = bpy.props.PointerProperty(type=CustomColorSet)
    bpy.types.Scene.custom_edit_color_set = bpy.props.PointerProperty(type=CustomColorSet)
    bpy.types.WindowManager.colorset_list_index = bpy.props.IntProperty(name="Index", default=0)
    bpy.types.Scene.turn_off_colorset_save = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.lock_colorset_color_changes = bpy.props.BoolProperty(default=True)

    bpy.app.handlers.load_post.append(loadColorPresets)
    
    from bpy.utils import register_class
    for cls in classes:
        try:
            register_class(cls)
        except:
            pass


def unregister():
    del bpy.types.WindowManager.widget_list
    del bpy.types.WindowManager.toggle_preview
    del bpy.types.Scene.bone_widget_colors
    del bpy.types.Scene.live_update_on
    del bpy.types.Scene.live_update_toggle
    del bpy.types.WindowManager.custom_color_presets
    del bpy.types.Scene.custom_pose_color_set
    del bpy.types.Scene.custom_edit_color_set
    del bpy.types.WindowManager.colorset_list_index
    del bpy.types.Scene.turn_off_colorset_save
    del bpy.types.Scene.lock_colorset_color_changes

    bpy.utils.unregister_class(PresetColorSetItem)
    bpy.utils.unregister_class(CustomColorSet)

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    
    from bpy.utils import unregister_class
    for cls in classes:
        try:
            unregister_class(cls)
        except:
            pass
