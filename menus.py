import bpy
from bpy.types import Menu

from .operators import BONEWIDGET_OT_createWidget, BONEWIDGET_OT_editWidget


class BONEWIDGET_MT_bw_specials(Menu):
    bl_label = "Bone Widget Specials"

    def draw(self, context):
        layout = self.layout
        layout.operator("bonewidget.add_widgets", icon="ADD", text="Add Widget to library")
        layout.operator("bonewidget.remove_widgets", icon="REMOVE",
                        text="Remove Widget from library")


class BONEWIDGET_MT_pie(Menu):
    bl_label = "Bone Widget Pie Menu"
    bl_idname = "BONEWIDGET_MT_pie"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()

        pie.operator(BONEWIDGET_OT_createWidget.bl_idname, icon='ADD', text=BONEWIDGET_OT_createWidget.bl_label)
        pie.operator(BONEWIDGET_OT_editWidget.bl_idname, icon='GREASEPENCIL', text=BONEWIDGET_OT_editWidget.bl_label)


classes = (
    BONEWIDGET_MT_bw_specials,
    BONEWIDGET_MT_pie,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
