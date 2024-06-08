import bpy
import bpy.utils.previews
from .jsonFunctions import readWidgets
import os


preview_collections = {}

def generate_previews():
    enum_items = []

    pcoll = preview_collections["widgets"]
    if pcoll.widget_list:
        return pcoll.widget_list
    
    #directory = os.path.join(os.path.dirname(__file__), "thumbnails")
    directory = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'thumbnails'))

    if directory and os.path.exists(directory):
        widget_names = sorted(readWidgets())

        for i, name in enumerate(widget_names):
            filepath = os.path.join(directory, name + ".png")

            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.widget_list = enum_items
    return enum_items


def preview_update(self, context):
    if len(bpy.types.Scene.widget_list.keywords["items"]) != len(bpy.types.WindowManager.widget_list.keywords["items"]):
        del bpy.types.WindowManager.widget_list
        for pcoll in preview_collections.values():
            bpy.utils.previews.remove(pcoll)
        preview_collections.clear()

        pcoll = bpy.utils.previews.new()
        pcoll.widget_list = ()
        preview_collections["widgets"] = pcoll
        
        bpy.types.WindowManager.widget_list = bpy.props.EnumProperty(
            items=generate_previews(), name="Shape", description="Shape", update=preview_update
        )