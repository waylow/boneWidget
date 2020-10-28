import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty

from .bl_class_registry import BlClassRegistry
from .panels import BONEWIDGET_PT_posemode_panel

@BlClassRegistry()
class BoneWidgetPreferences(AddonPreferences):
    bl_idname = __package__

    # widget prefix
    widget_prefix: StringProperty(
        name="Bone Widget prefix",
        description="Choose a prefix for the widget objects",
        default="WDGT_",
    )
    '''
    #symmetry suffix (will try to implement this later)
    symmetry_suffix: EnumProperty(
        name="Bone Widget symmetry suffix",
        description="Choose a naming convention for the symmetrical widgets",
        default=".L",
    )
    '''
    # collection name
    bonewidget_collection_name: StringProperty(
        name="Bone Widget collection name",
        description="Choose a name for the collection the widgets will appear",
        default="WDGT_shapes",
    )

    def panel_category_update_fn(self, context):
        has_panel = hasattr(bpy.types, BONEWIDGET_PT_posemode_panel.bl_idname)
        if has_panel:
            try:
                bpy.utils.unregister_class(BONEWIDGET_PT_posemode_panel)
            except:
                pass
        BONEWIDGET_PT_posemode_panel.bl_category = self.panel_category
        bpy.utils.register_class(BONEWIDGET_PT_posemode_panel)

    panel_category = bpy.props.StringProperty(
        name="Category",
        description="Category to show Bone-Widgets panel",
        default="Rig Tools",
        update=panel_category_update_fn,
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.prop(self, "widget_prefix", text="Widget Prefix")
#        add symmetry suffix later
#        col.prop(self, "symmetry_suffix", text="Symmetry suffix")
        col.prop(self, "bonewidget_collection_name", text="Collection name")

        row = layout.row()

        row = layout.row()
        col = row.column()
        col.label(text="Set the category to show Bone-Widgets panel:")
        col.prop(self, "panel_category")
