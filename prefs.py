import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty

from .panels import BONEWIDGET_PT_bw_panel_main
from .operators import BONEWIDGET_OT_reset_default_images, BONEWIDGET_OT_user_data_filebrowser
from .props import BW_ColorPanel


class BONEWIDGET_UL_panel_order(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name)

        icon_name = "HIDE_ON" if not item.enabled else "HIDE_OFF"
        row.prop(item, "enabled", text="", icon=icon_name, toggle=True)


class BONEWIDGET_OT_move_color_panel(bpy.types.Operator):
    bl_idname = "bonewidget.move_color_panel"
    bl_label = "Move Color Panel"

    direction: bpy.props.EnumProperty(
        items=[
            ('UP', "Up", ""),
            ('DOWN', "Down", "")
        ]
    )

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        idx = prefs.panel_order_index

        if self.direction == 'UP':
            if idx > 0:
                prefs.panel_order.move(idx, idx - 1)
                prefs.panel_order_index -= 1

        elif self.direction == 'DOWN':
            if idx < len(prefs.panel_order) - 1:
                prefs.panel_order.move(idx, idx + 1)
                prefs.panel_order_index += 1

        return {'FINISHED'}


class BoneWidget_preferences(AddonPreferences):
    bl_idname = __package__

    # Use Rigify Defaults
    use_rigify_defaults: BoolProperty(
        name="Use Rigify Defaults",
        description="Use the same naming convention for widget creation (disable if you prefer your naming convention)",
        default=True,
    )

    # widget prefix
    widget_prefix: StringProperty(
        name="Bone Widget prefix",
        description="Choose a prefix for the widget objects",
        default="WGT-",
    )

    # symmetry suffix
    symmetry_suffix: StringProperty(
        name="Bone Widget symmetry suffix",
        description="Choose a naming convention for the symmetrical widgets, separate by semicolon.",
        default="L; R",
    )

    # collection name
    bonewidget_collection_name: StringProperty(
        name="Bone Widget collection name",
        description="Choose a name for the collection the widgets will appear",
        default="WGTS",
    )

    def panel_category_update_fn(self, context):
        has_panel = hasattr(bpy.types, BONEWIDGET_PT_bw_panel_main.bl_idname)
        if has_panel:
            try:
                bpy.utils.unregister_class(BONEWIDGET_PT_bw_panel_main)
            except:
                pass
        BONEWIDGET_PT_bw_panel_main.bl_category = self.panel_category
        bpy.utils.register_class(BONEWIDGET_PT_bw_panel_main)

    panel_category: StringProperty(
        name="Panel Category",
        description="Category to show Bone-Widgets panel",
        default="Rigging",
        update=panel_category_update_fn,
    )

    preview_panel_size: FloatProperty(
        name="Preview Panel Size",
        description="Size of the Preview Panel",
        default=6.0,
        min=1.0,
        max=10.0,
        precision=1,
    )

    preview_popup_size: FloatProperty(
        name="Preview Popup Size",
        description="Size of the Preview Popup Thumbnails",
        default=3.5,
        min=1.0,
        max=10.0,
        precision=1,
    )

    preview_default: BoolProperty(
        name="Default Preview State",
        description="Default state of preview panel",
        default=True,
    )

    edit_bone_colors: EnumProperty(
        name="Edit Bone Colors",
        description="Behavior of Edit Bone colors",
        items=[
            ('DEFAULT', "Default", "Set the Edit Bone color to the default colors"),
            ('LINKED', "Linked",
             "Use the same colors for both the Edit bones and Pose bones"),
            ('SEPARATE', "Separate",
             "Edit bones and Pose bones will have their own colors"),
        ],
        default='DEFAULT'
    )

    clear_both_modes: BoolProperty(
        name="Clear All Bone Color",
        description='When enabled, bone colors from Edit mode and Pose mode will be cleared.  When disabled, only the color from the current mode will be cleared',
        default=True
    )

    symmetrize_color: BoolProperty(
        name="Symmetrize Bone Colors",
        description='When enabled, bone colors will be copied when you symmetrize a widget. When disabled, only the shape will be symmetrized',
        default=True
    )

    copy_color: BoolProperty(
        name="Copy Bone Colors",
        description='When enabled, bone colors will be copied when you copy a widget. When disabled, only the shape will be copied',
        default=True
    )

    use_default_location: BoolProperty(
        name="Use Default Location",
        description='When enabled, user widgets and color sets will be saved to extensions/.user/{repository_name}/bone_widget/bone_widget_custom_data',
        default=True
    )

    user_data_location: StringProperty(
        name="User Data Location",
        description="Choose a location where you want to save custom data",
        default="",
    )

    # panel order
    panel_order: bpy.props.CollectionProperty(type=BW_ColorPanel)
    panel_order_index: bpy.props.IntProperty()

    reset_custom_shape_transforms: BoolProperty(
        name="Reset Custom Shape Transforms",
        description='When enabled, any transforms to the custom shape will be reset to default when adding a new widget. This will force your new widget to display exactly as expected.',
        default=True
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Widget Naming Convention:")
        box.prop(self, "use_rigify_defaults", text="Use Rigify Defaults")

        box_row = box.row()
        box_col = box_row.column()
        box_col.prop(self, "widget_prefix", text="Widget Prefix")
        box_col.prop(self, "bonewidget_collection_name",
                     text="Collection name")
        box_row.enabled = not self.use_rigify_defaults

        box_row = box.row()
        box_row = box.row()
        box_row.prop(self, "symmetry_suffix", text="Symmetry suffix")

        row = layout.row()

        box = layout.box()
        box_col = box.column()
        box_col.label(text="Set the category to show Bone-Widgets panel:")
        box_col.prop(self, "panel_category")

        # edit bone colors
        row = layout.row()
        box = layout.box()
        box.label(text="Bone Color Behavior:")
        row = box.row()
        row.prop(self, "edit_bone_colors")
        row = box.row()
        row.label(text="Clearing Colors:")
        row.prop(self, "clear_both_modes")
        row = box.row()
        row.label(text="Symmetrize Colors:")
        row.prop(self, "symmetrize_color")
        row = box.row()
        row.label(text="Copy Colors:")
        row.prop(self, "copy_color")

        # preview area
        row = layout.row()
        box = layout.box()

        box.label(text="Thumbnail Previews:")
        box_row = box.row()
        box_row.prop(self, "preview_default",
                     text="Display Previews by Default")

        box_row = box.row()
        box_col = box_row.column()
        box_col.label(text="Preview Panel Size:")
        box_row.prop(self, "preview_panel_size", text="")

        box_row = box.row()
        box_col = box_row.column()
        box_col.label(text="Preview Popup Size:")
        box_row.prop(self, "preview_popup_size", text="")

        # custom data
        row = layout.row()
        box = layout.box()

        box.label(text="Custom Data:")
        box_row = box.row()
        box_row.prop(self, "use_default_location", text="Use Default Location")

        box_row = box.row()
        box_col = box_row.column()
        box_col.prop(self, "user_data_location", text="Custom Path")
        box_row.operator("bonewidget.user_data_filebrowser",
                         icon="FILEBROWSER", text="")
        box_row.enabled = not self.use_default_location

        # reset custom shape transforms
        box = layout.box()
        box.label(text="Reset Transforms:")
        box.prop(self, "reset_custom_shape_transforms",
                 text="Reset Custom Shape Transforms")

        # panel order
        row = layout.row()
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Color Panel Order:")

        list_col = row.column()
        list_col.template_list(
            "BONEWIDGET_UL_panel_order",
            "",
            self,
            "panel_order",
            self,
            "panel_order_index",
            rows=2,
            sort_lock=True,
        )

        btn_col = row.column(align=True)
        op = btn_col.operator("bonewidget.move_color_panel", icon="TRIA_UP", text="")
        op.direction = 'UP'
        op = btn_col.operator("bonewidget.move_color_panel", icon="TRIA_DOWN", text="")
        op.direction = 'DOWN'

        # reset button
        layout.separator()
        row = layout.row()
        row = row.split(factor=.75)
        row.label(text="Reset Default Widget Thumbnails")
        row.operator("bonewidget.reset_default_images", icon="ERROR")


classes = (
    BW_ColorPanel,
    BONEWIDGET_UL_panel_order,
    BONEWIDGET_OT_move_color_panel,
    BoneWidget_preferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # add panels to the list and perform a sanity check to ensure
    # the list is always in sync with the actual panels available
    prefs = bpy.context.preferences.addons[__package__].preferences

    # the panels to show in the UI list, with their default order
    expected_panels = [
        ("BONEWIDGET_PT_bw_custom_color_presets", "Custom Color Presets"),
        ("BONEWIDGET_PT_bw_blender_color_set", "Blender Color Sets"),
    ]

    # map panel_id to default index
    default_index = {pid: i for i, (pid, _) in enumerate(expected_panels)}

    # track IDs
    existing_ids = {entry.panel_id for entry in prefs.panel_order}

    # add missing panels
    for pid, name in expected_panels:
        if pid not in existing_ids:
            # decide where to insert the new panel based on its default index
            target_default_index = default_index[pid]

            # count how many have a lower default index
            insert_at = sum(
                1 for entry in prefs.panel_order
                if default_index.get(entry.panel_id, 9999) < target_default_index
            )

            # add missing panels at the end first
            new = prefs.panel_order.add()
            new.panel_id = pid
            new.name = name
            new.enabled = True
            new.expanded = True

            # move it to the correct position
            prefs.panel_order.move(len(prefs.panel_order) - 1, insert_at)

    # remove any panels that no longer exist
    expected_ids = {pid for pid, _ in expected_panels}
    for i in reversed(range(len(prefs.panel_order))):
        if prefs.panel_order[i].panel_id not in expected_ids:
            prefs.panel_order.remove(i)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
