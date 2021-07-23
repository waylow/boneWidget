from bpy.types import Menu

from . import functions, panels


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
            # left, right, bottom, top
            pie.operator("bonewidget.create_widget", icon="OBJECT_DATAMODE")
            pie.operator("bonewidget.edit_widget", icon="GREASEPENCIL")
            pie.operator("bonewidget.clear_widgets", icon="X")
            pie.prop(context.scene, "widget_list", expand=False, text="")

            # topleft, topright, bottomleft, bottomright
            pie.operator("bonewidget.copy_widget", icon="DUPLICATE")
            collection = functions.getViewLayerCollection(context, query=True)
            if collection is None:
                pie.separator()
            else:
                icon, text = panels.widgetDataFromVisibility(collection.hide_viewport)
                pie.operator("bonewidget.toggle_collection_visibilty", icon=icon, text=text)
            pie.operator("bonewidget.delete_unused_widgets", icon="TRASH")
        elif context.mode in {"OBJECT", "EDIT"}:
            pie.separator()
            pie.operator("bonewidget.return_to_armature", icon="LOOP_BACK", text="To Bone")
