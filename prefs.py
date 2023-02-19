import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty

from .bl_class_registry import BlClassRegistry
from .panels import VIEW3D_PT_bw_panel_main


@BlClassRegistry()
class BoneWidgetPreferences(AddonPreferences):
    bl_idname = __package__

    #Use Rigify Defaults
    use_rigify_defaults: BoolProperty(
        name="Use Rigify Defaults",
        description="Use the same naming convention for widget creation (disable if you prefer your naming convention)",
        default=False,
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
        has_panel = hasattr(bpy.types, VIEW3D_PT_bw_panel_main.bl_idname)
        if has_panel:
            try:
                bpy.utils.unregister_class(VIEW3D_PT_bw_panel_main)
            except:
                pass
        VIEW3D_PT_bw_panel_main.bl_category = self.panel_category
        bpy.utils.register_class(VIEW3D_PT_bw_panel_main)

    panel_category: bpy.props.StringProperty(
        name="Panel Category",
        description="Category to show Bone-Widgets panel",
        default="Rigging",
        update=panel_category_update_fn,
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "use_rigify_defaults", text="Use Rigify Defaults")

        row = layout.row()
        col = row.column()
        col.prop(self, "widget_prefix", text="Widget Prefix")
        col.prop(self, "bonewidget_collection_name", text="Collection name")
        row.enabled = not self.use_rigify_defaults

        row = layout.row()
        row = layout.row()
        row.prop(self, "symmetry_suffix", text="Symmetry suffix")

        row = layout.row()

        row = layout.row()
        col = row.column()
        col.label(text="Set the category to show Bone-Widgets panel:")
        col.prop(self, "panel_category")
