import bpy
import bpy.utils.previews
from .props import PresetColorSetItem
from .functions.main_functions import (
    recursive_layer_collection,
    get_preferences,
)
from .functions.preview_functions import (
    create_preview_collection,
    preview_collections,
    get_preview_default,
)
from .functions.json_functions import load_color_presets

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

    def draw(self, context):
        if context.window_manager.load_presets_on_startup:
            load_color_presets()
            context.window_manager.load_presets_on_startup = False

        # cache call to get preferences
        preferences = get_preferences(context)

        layout = self.layout

        # preview toggle checkbox
        row = layout.row(align=True)
        row.prop(context.window_manager, "toggle_preview")

        # preview view
        if context.window_manager.toggle_preview:
            row = layout.row(align=True)
            preview_panel_size = preferences.preview_panel_size
            preview_popup_size = preferences.preview_popup_size
            row.template_icon_view(context.window_manager, "widget_list", show_labels=True,
                                   scale=preview_panel_size, scale_popup=preview_popup_size)

        # dropdown list
        row = layout.row(align=True)
        row.prop(context.window_manager, "widget_list", expand=False, text="")

        row = layout.row(align=True)
        row.menu("BONEWIDGET_MT_bw_specials", icon='DOWNARROW_HLT', text="")
        row.operator("bonewidget.create_widget",
                     icon="OBJECT_DATAMODE", text="Create")

        if context.mode == "POSE":
            row.operator("bonewidget.edit_widget", icon="OUTLINER_DATA_MESH")
        else:
            row.operator("bonewidget.return_to_armature",
                         icon="LOOP_BACK", text='To bone')

        layout.separator()

        # 1ST BLOCK
        # Symmetry button | (include color)
        col = layout.column(align=True)

        row = col.row(align=True)
        row.operator("bonewidget.symmetrize_shape",
                     icon='MOD_MIRROR', text="Symmetrize Shape")
        icon = 'RESTRICT_COLOR_OFF'
        if preferences.symmetrize_color:
            icon = 'RESTRICT_COLOR_ON'
        row.prop(preferences, "symmetrize_color",
                 icon=icon, text='', toggle=True)

        # Copy Widget | (include color)
        row = col.row(align=True)
        row.operator("bonewidget.copy_bone_widget",
                     icon='COPYDOWN', text="Copy Widget")
        copy_color_icon = 'RESTRICT_COLOR_ON' if preferences.copy_color else 'RESTRICT_COLOR_OFF'
        row.prop(preferences, "copy_color",
                 icon=copy_color_icon, text='', toggle=True)

        layout.separator()
        # 2ND BLOCK
        # Match Transforms | Resync Names
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("bonewidget.match_bone_transforms",
                     icon='GROUP_BONE', text="Match Transforms")

        row.operator("bonewidget.resync_widget_names",
                     icon='FILE_REFRESH', text='')

        # Clear Widgets | Delete Unused
        row = col.row(align=True)
        row.operator("bonewidget.clear_widgets",
                     icon='X', text="Clear Widget(s)")

        row.operator("bonewidget.delete_unused_widgets",
                     icon='TRASH', text='')

        # if the bw collection exists, show the visibility toggle
        bw_collection_name = None
        if not preferences.use_rigify_defaults:
            bw_collection_name = preferences.bonewidget_collection_name
        elif context.active_object:
            bw_collection_name = 'WGTS_' + context.active_object.name

        bw_collection = recursive_layer_collection(
            context.view_layer.layer_collection, bw_collection_name)

        # Hide Collection Button
        text = "Hide Collection"
        icon = "HIDE_OFF"
        collection_found = False
        if bw_collection is not None:
            collection_found = True
            if bw_collection.hide_viewport:
                icon = "HIDE_ON"
                text = "Show Collection"

        row = col.row(align=True)
        row.operator("bonewidget.toggle_collection_visibilty",
                     icon=icon, text=text)
        # disable this button if the collection doesn't exist
        row.enabled = collection_found

        layout.separator()
        # 3RD BLOCK
        # Use Selected Object
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("bonewidget.add_as_widget",
                     text="Use Selected Object",
                     icon='RESTRICT_SELECT_OFF')

        # bone colors
        if bpy.app.version >= (4, 0, 0):
            layout.separator()
            col = layout.column(align=True)

            # Copy Color to Selected
            row = col.row(align=True)
            row.operator("bonewidget.copy_color_to_selected",
                         text="Copy Color", icon="RESTRICT_COLOR_ON")

            # Clear Bone Color
            row = col.row(align=True)
            row.operator("bonewidget.clear_bone_color",
                         text="Clear Bone Color", icon="PANEL_CLOSE")

            icon = 'GROUP_BONE' if preferences.clear_both_modes else 'BONE_DATA'
            row.prop(preferences, "clear_both_modes",
                     icon=icon, text='', toggle=True)


class BONEWIDGET_PT_bw_custom_color_presets(BONEWIDGET_PT_bw_panel, bpy.types.Panel):

    bl_idname = "BONEWIDGET_PT_bw_custom_color_presets"
    bl_parent_id = "BONEWIDGET_PT_bw_panel_main"
    bl_label = "Custom Color Presets"

    @classmethod
    def poll(self, context):
        return bpy.app.version >= (4, 0, 0)

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.template_list("BONEWIDGET_UL_colorset_items", "", context.window_manager, "custom_color_presets",
                          context.window_manager, "colorset_list_index")

        col = row.column(align=True)
        col.operator("bonewidget.add_default_custom_colorset",
                     icon='ADD', text="")
        col.operator("bonewidget.remove_custom_item", icon='REMOVE', text="")
        col.separator()
        col.menu("BONEWIDGET_MT_bw_color_presets_specials",
                 icon="DOWNARROW_HLT", text="")
        col.separator()
        col.operator("bonewidget.move_custom_item",
                     icon="TRIA_UP", text="").direction = "UP"
        col.operator("bonewidget.move_custom_item",
                     icon="TRIA_DOWN", text="").direction = "DOWN"
        row = layout.row()
        row.operator("bonewidget.add_colorset_to_bone",
                     text="Apply To Selected Bones")


class BONEWIDGET_UL_colorset_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        # set the size of each color set field
        split = layout.split(factor=0.58)
        split.prop(item, "name", text="", emboss=False)

        row = split.row(align=True)
        row.prop(item, "normal", text="")
        row.prop(item, "select", text="")
        row.prop(item, "active", text="")


class BONEWIDGET_PT_bw_blender_color_set(BONEWIDGET_PT_bw_panel, bpy.types.Panel):

    bl_idname = "BONEWIDGET_PT_bw_blender_color_set"
    bl_parent_id = "BONEWIDGET_PT_bw_panel_main"
    bl_label = "Blender Color Sets"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return bpy.app.version >= (4, 0, 0)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        # Bone Theme Colors
        row = col.row(align=True)
        row.operator("bonewidget.set_bone_color",
                     text="Set Bone Color", icon="BRUSHES_ALL")
        row.scale_x = 3.0
        icon_row = row.row()
        icon_row.enabled = (context.object is not None and context.object.type == 'ARMATURE' and
                            context.object.mode in {'POSE', 'EDIT'})
        icon_row.template_icon_view(
            context.scene.bw_settings, "bone_widget_colors",
            show_labels=False, scale=1, scale_popup=1.8)

        # custom color sets
        if context.scene.bw_settings.bone_widget_colors == "CUSTOM":
            custom_pose_color = context.scene.bw_settings.custom_pose_color_set
            custom_edit_color = context.scene.bw_settings.custom_edit_color_set

            col = layout.column(align=True)

            # pose bone colors
            if context.object.mode == 'POSE':
                row = col.row(align=True)
                row.prop(custom_pose_color, "normal", text="")
                row.prop(custom_pose_color, "select", text="")
                row.prop(custom_pose_color, "active", text="")
                row.separator(factor=0.5)
                row.prop(context.scene.bw_settings, "live_update_toggle",
                         text="", icon="UV_SYNC_SELECT")
            # edit bone colors
            elif context.object.mode == "EDIT" and preferences.edit_bone_colors != 'DEFAULT':
                row = col.row(align=True)
                row.prop(custom_edit_color, "normal", text="")
                row.prop(custom_edit_color, "select", text="")
                row.prop(custom_edit_color, "active", text="")
                row.separator(factor=0.5)
                row.prop(context.scene.bw_settings, "live_update_toggle",
                         text="", icon="UV_SYNC_SELECT")

            col = layout.column(align=True)
            col.operator("bonewidget.copy_color_to_palette",
                         text="Copy Color to Palette", icon="COPYDOWN")


classes = (
    BONEWIDGET_PT_bw_panel_main,
    BONEWIDGET_PT_bw_custom_color_presets,
    BONEWIDGET_UL_colorset_items,
    BONEWIDGET_PT_bw_blender_color_set,
)


def register():
    if not hasattr(bpy.types.WindowManager, "widget_list"):
        create_preview_collection()

    bpy.types.WindowManager.toggle_preview = bpy.props.BoolProperty(
        name="Preview Panel",
        default=get_preview_default(),
        description="Show thumbnail previews"
    )

    bpy.utils.register_class(PresetColorSetItem)
    bpy.types.WindowManager.custom_color_presets = bpy.props.CollectionProperty(
        type=PresetColorSetItem)
    bpy.types.WindowManager.colorset_list_index = bpy.props.IntProperty(
        name="Index", default=0)
    bpy.types.WindowManager.turn_off_colorset_save = bpy.props.BoolProperty(
        name="Turn Off ColorSet Save",
        description="Disable automatic saving of color sets",
        default=False
    )
    bpy.types.WindowManager.load_presets_on_startup = bpy.props.BoolProperty(
        name="Load Presets on Startup",
        description="Load color presets when Blender starts",
        default=True
    )

    from bpy.utils import register_class
    for cls in classes:
        try:
            register_class(cls)
        except:
            pass


def unregister():
    if hasattr(bpy.types.WindowManager, "widget_list"):
        del bpy.types.WindowManager.widget_list

    del bpy.types.WindowManager.toggle_preview
    del bpy.types.WindowManager.custom_color_presets
    del bpy.types.WindowManager.colorset_list_index
    del bpy.types.WindowManager.turn_off_colorset_save
    del bpy.types.WindowManager.load_presets_on_startup

    bpy.utils.unregister_class(PresetColorSetItem)

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    from bpy.utils import unregister_class
    for cls in classes:
        try:
            unregister_class(cls)
        except:
            pass
