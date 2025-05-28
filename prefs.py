import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty

from .bl_class_registry import BlClassRegistry
from .panels import BONEWIDGET_PT_bw_panel_main
from .operators import BONEWIDGET_OT_reset_default_images


@BlClassRegistry()
class BoneWidget_preferences(AddonPreferences):
    bl_idname = __package__

    #Use Rigify Defaults
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
        description="Choose a naming convention for the symmetrical widgets, seperate by semicolon.",
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
            ('LINKED', "Linked", "Use the same colors for both the Edit bones and Pose bones"),
            ('SEPARATE', "Separate", "Edit bones and Pose bones will have their own colors"),
        ],
        default='DEFAULT'
    )
    

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, "use_rigify_defaults", text="Use Rigify Defaults")

        box_row = box.row()
        box_col = box_row.column()
        box_col.prop(self, "widget_prefix", text="Widget Prefix")
        box_col.prop(self, "bonewidget_collection_name", text="Collection name")
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
        box.label(text="Edit Bone Color Behavior:")
        row = box.row()
        row.prop(self, "edit_bone_colors")

        # preview area
        row = layout.row()
        box = layout.box()
        
        box.label(text="Thumbnail Previews:")
        box_row = box.row()
        box_row.prop(self, "preview_default", text="Display Previews by Default")

        box_row = box.row()
        box_col = box_row.column()
        box_col.label(text="Preview Panel Size:")
        box_row.prop(self, "preview_panel_size", text="")
        
        box_row = box.row()
        box_col = box_row.column()
        box_col.label(text="Preview Popup Size:")
        box_row.prop(self, "preview_popup_size", text="")

        layout.separator()
        row = layout.row()
        row = row.split(factor=.75)
        row.label(text="Reset Default Widget Thumbnails")
        row.operator("bonewidget.reset_default_images", icon="ERROR")
