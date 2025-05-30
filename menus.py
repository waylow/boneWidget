from bpy.types import Menu

class BONEWIDGET_MT_bw_specials(Menu):
    bl_label = "Bone Widget Specials"

    def draw(self, context):
        layout = self.layout
        layout.operator("bonewidget.add_widgets", icon="ADD", text="Add Widget to Library")
        layout.operator("bonewidget.remove_widgets", icon="REMOVE",
                        text="Remove Widget from Library")
        layout.separator()
        layout.operator("bonewidget.add_custom_image", icon="FILE_IMAGE",
                        text="Add Custom Image to Widget")
        layout.operator("bonewidget.render_widget_thumbnail", icon="RESTRICT_RENDER_OFF",
                        text="Render object as thumbnail")
        layout.separator()
        layout.operator("bonewidget.import_library", icon="IMPORT", text="Import Widget Library")
        layout.operator("bonewidget.export_library", icon="EXPORT", text="Export Widget Library")


class BONEWIDGET_MT_bw_color_presets_specials(Menu):
    bl_label = "Color Presets Specials"

    def draw(self, context):
        layout = self.layout
        btn_text = "Add Preset from Theme" if "THEME" in context.scene.bone_widget_colors else "Add Preset from Palette"
        layout.operator("bonewidget.add_color_set_from", text=btn_text, icon="ADD")
        layout.operator("bonewidget.add_preset_from_bone", icon="ADD", text="Add Preset from Bone")     
        layout.separator()
        layout.operator("bonewidget.export_color_presets", icon="EXPORT", text="Export Color Presets")   


classes = (
    BONEWIDGET_MT_bw_specials,
    BONEWIDGET_MT_bw_color_presets_specials,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
