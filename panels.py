import bpy
import bpy.utils.previews
from .props import PresetColorSetItem
from .functions.main_functions import (
    recursive_layer_collection,
    get_preferences,
)
from .functions.preview_functions import (
    create_preview_collection,
    refresh_widget_list,
    preview_collections,
    get_preview_default,
)
from .functions.json_functions import load_color_presets

from .menus import BONEWIDGET_MT_bw_specials


def bw_filter_mode_update(self, context):
    # update the preview collection based on the new filter mode
    # restore the current widget selection if possible,
    # otherwise reset to first item
    current_widget = context.window_manager.widget_list
    refresh_widget_list()
    items = bpy.types.WindowManager.widget_list.keywords['items']
    found_same_widget = any(current_widget == item[0] for item in items)
    if not found_same_widget:
        context.window_manager.widget_list = items[0][0] if items else ""
    else:
        context.window_manager.widget_list = current_widget
    

class BONEWIDGET_PT_bw_panel:
    """BoneWidget Addon UI"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rigging"
    bl_label = "Bone Widget"


class BONEWIDGET_PT_bw_master_panel(BONEWIDGET_PT_bw_panel, bpy.types.Panel):
    bl_idname = 'BONEWIDGET_PT_bw_master_panel'

    def draw(self, context):
        pass


class BONEWIDGET_PT_bw_panel_main(BONEWIDGET_PT_bw_panel, bpy.types.Panel):
    bl_idname = 'BONEWIDGET_PT_bw_panel_main'
    bl_label = "Widget Library"

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

        # filter mode toggle
        row.prop(
            context.window_manager,
            "bw_enable_filter_panel",
            text="",
            icon='FILTER',
            toggle=True
        )

        # ------------------------------------------------------------
        # FILTER PANEL
        # Only visible when search mode is enabled
        # ------------------------------------------------------------
        if context.window_manager.bw_enable_filter_panel:
            box = layout.box()
            col = box.column(align=True)

            # horizontal enum buttons
            row = col.row(align=True)
            row.prop(context.window_manager, "bw_filter_mode", expand=True)

            col.separator()

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
        split = row.split(factor=0.75, align=True)

        left = split.row(align=True)
        left.operator(
            "bonewidget.match_bone_transforms",
            icon='GROUP_BONE',
            text="Match Transforms"
        )

        right = split.row(align=True)
        right.operator(
            "bonewidget.resync_widget_names",
            icon='FILE_REFRESH',
            text="Resync"
        )

        # Clear | Delete
        row = col.row(align=True)
        split = row.split(factor=0.75, align=True)

        left = split.row(align=True)
        left.operator(
            "bonewidget.clear_widgets",
            icon='X',
            text="Clear Widget(s)"
        )

        right = split.row(align=True)
        right.operator(
            "bonewidget.delete_unused_widgets",
            icon='TRASH',
            text="Delete"
        )

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
    bl_label = "Custom Color Presets"
    #bl_parent_id = "BONEWIDGET_PT_bw_panel_main"

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
    bl_label = "Blender Color Sets"
    #bl_parent_id = "BONEWIDGET_PT_bw_panel_main"

    @classmethod
    def poll(self, context):
        return bpy.app.version >= (4, 0, 0)

    def draw(self, context):
        preferences = get_preferences(context)

        layout = self.layout
        bw_settings = context.scene.bw_settings
        obj = context.object

        row = layout.row(align=True)

        row.operator(
            "bonewidget.set_bone_color",
            text="Apply Color Theme",
            icon="BRUSHES_ALL"
        )

        icon_row = row.row()
        icon_row.enabled = (
            obj is not None
            and obj.type == 'ARMATURE'
            and obj.mode in {'POSE', 'EDIT'}
        )
        icon_row.template_icon_view(
            bw_settings,
            "bone_widget_colors",
            show_labels=False,
            scale=1,
            scale_popup=1.8
        )

        layout.separator()

        col = layout.column(align=True)

        custom_pose_color = bw_settings.custom_pose_color_set
        custom_edit_color = bw_settings.custom_edit_color_set

        show_live_button = False

        if obj is not None and obj.mode == 'POSE':
            row = col.row(align=True)
            row.prop(custom_pose_color, "normal", text="")
            row.prop(custom_pose_color, "select", text="")
            row.prop(custom_pose_color, "active", text="")
            row.separator(factor=0.5)
            show_live_button = True

        elif (
            obj is not None
            and obj.mode == "EDIT"
            and preferences.edit_bone_colors != 'DEFAULT'
        ):
            row = col.row(align=True)
            row.prop(custom_edit_color, "normal", text="")
            row.prop(custom_edit_color, "select", text="")
            row.prop(custom_edit_color, "active", text="")
            row.separator(factor=0.5)
            show_live_button = True

        if show_live_button:
            row.prop(
                bw_settings,
                "live_update_toggle",
                text="",
                icon="UV_SYNC_SELECT"
            )
        
        col_buttons = layout.column(align=True)

        col_buttons.operator(
            "bonewidget.copy_color_to_palette",
            text="Copy Color to Palette",
        icon="COPYDOWN"
        )

        col_buttons.operator(
            "bonewidget.set_bone_color",
            text="Set Bone Color",
            icon="BRUSHES_ALL"
        )


classes = (
    BONEWIDGET_UL_colorset_items,
)

panel_classes = {
    "BONEWIDGET_PT_bw_panel_main": BONEWIDGET_PT_bw_panel_main,
    "BONEWIDGET_PT_bw_custom_color_presets": BONEWIDGET_PT_bw_custom_color_presets,
    "BONEWIDGET_PT_bw_blender_color_set": BONEWIDGET_PT_bw_blender_color_set,
}


def register_panels():
    prefs = bpy.context.preferences.addons[__package__].preferences

    # unregister master panel first
    try:
        bpy.utils.unregister_class(BONEWIDGET_PT_bw_master_panel)
    except RuntimeError:
        pass

    # unregister all sub panels
    for panel_cls in panel_classes.values():
        try:
            bpy.utils.unregister_class(panel_cls)
        except RuntimeError:
            pass

    # register master panel with category name
    BONEWIDGET_PT_bw_master_panel.bl_category = prefs.panel_category
    bpy.utils.register_class(BONEWIDGET_PT_bw_master_panel)

    # re-register the sub panels in user-defined order
    for panel in prefs.panel_order:
        if not panel.enabled:
            continue

        panel_cls = panel_classes.get(panel.panel_id)
        if not panel_cls:
            continue

        # make this panel a child of the master panel
        panel_cls.bl_parent_id = "BONEWIDGET_PT_bw_master_panel"

        # apply expanded/collapsed state
        panel_cls.bl_options = set() if panel.expanded else {'DEFAULT_CLOSED'}

        bpy.utils.register_class(panel_cls)


def register():
    bpy.types.WindowManager.bw_filter_mode = bpy.props.EnumProperty(
        name="Filter Mode",
        items=[
            ('ALL', "All", "Show all widgets"),
            ('BUILTIN', "Built-In", "Show built-in widgets"),
            ('CUSTOM', "Custom", "Show custom widgets"),
        ],
        default='ALL',
        update=bw_filter_mode_update,
    )

    bpy.types.WindowManager.bw_enable_filter_panel = bpy.props.BoolProperty(
        name="Enable Search",
        description="Show search filter options",
        default=False,
        update=bw_filter_mode_update,
    )

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

    register_panels()


def unregister():
    if hasattr(bpy.types.WindowManager, "widget_list"):
        del bpy.types.WindowManager.widget_list

    del bpy.types.WindowManager.bw_filter_mode
    del bpy.types.WindowManager.bw_enable_filter_panel
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

    for cls in panel_classes.values():
        try:
            unregister_class(cls)
        except:
            pass
