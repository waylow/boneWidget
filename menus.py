from bpy.types import Menu


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

        if context.mode == "POSE":
            pie.operator("bonewidget.create_widget", icon="OBJECT_DATAMODE")
            pie.operator("bonewidget.edit_widget", icon="GREASEPENCIL")
            pie.operator("bonewidget.clear_widgets", icon="X")
            pie.prop(context.scene, "widget_list", expand=False, text="")
            pie.operator("bonewidget.delete_unused_widgets", icon="TRASH")
        elif context.mode in {"OBJECT", "EDIT"}:
            pie.separator()
            pie.operator("bonewidget.return_to_armature", icon="LOOP_BACK", text="To Bone")
