import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, FloatProperty

from .bl_class_registry import BlClassRegistry
from .panels import BONEWIDGET_PT_bw_panel_main


@BlClassRegistry()
class BoneWidgetPreferences(AddonPreferences):
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
        col.label(text="Set the name of the tab where the Bone-Widget addon will show:")
        col.prop(self, "panel_category")

        # preview area
        row = layout.row()
        row = layout.row()
        
        row.label(text="Thumbnail Previews:")
        row = layout.row()
        row.prop(self, "preview_default", text="Display Previews by Default")

        row = layout.row()
        col = row.column()
        col.label(text="Preview Panel Size:")
        row.prop(self, "preview_panel_size", text="")
        
        row = layout.row()
        col = row.column()
        col.label(text="Preview Popup Size:")
        row.prop(self, "preview_popup_size", text="")
        row = layout.row()
