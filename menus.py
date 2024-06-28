from bpy.types import Menu

class BONEWIDGET_MT_bw_specials(Menu):
    bl_label = "Bone Widget Specials"

    def draw(self, context):
        layout = self.layout
        layout.operator("bonewidget.add_widgets", icon="ADD", text="Add Widget to library")
        layout.operator("bonewidget.remove_widgets", icon="REMOVE",
                        text="Remove Widget from library")
        layout.separator()
        layout.operator("bonewidget.import_library", icon="IMPORT", text="Import Widget Library")
        layout.operator("bonewidget.export_library", icon="EXPORT", text="Export Widget Library")


classes = (
    BONEWIDGET_MT_bw_specials,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
