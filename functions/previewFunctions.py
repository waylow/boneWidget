import bpy
import bpy.utils.previews
from .jsonFunctions import readWidgets, getWidgetData, JSON_USER_WIDGETS
import os
from .. import __package__

preview_collections = {}


def createPreviewCollection():
    if preview_collections:
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


def generate_previews():
    enum_items = []

    pcoll = preview_collections["widgets"]
    if pcoll.widget_list:
        return pcoll.widget_list
    
    #directory = os.path.join(os.path.dirname(__file__), "thumbnails")
    directory = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'thumbnails'))
    custom_directory = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'custom_thumbnails'))

    if directory and os.path.exists(directory):
        widget_data = {item[0]: item[1].get("image", "missing_image.png") for item in readWidgets().items()}
        widget_names = sorted(widget_data.keys())

        for i, name in enumerate(widget_names):
            image = widget_data.get(name, "")
            filepath = os.path.join(directory, image)

            # try in custom_thumbnails if above failed
            if not os.path.exists(filepath):
                filepath = os.path.join(custom_directory, image)

            # if image still not found, let the user know
            if not os.path.exists(filepath):
                filepath = os.path.join(directory, "missing_image.png")

            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
                
            face_data_info = "Contains Face Data" if getWidgetData(name).get("faces") else ""
            enum_items.append((name, name, face_data_info, thumb.icon_id, i))
    
    pcoll.widget_list = enum_items
    return enum_items


def preview_update(self, context):
    generate_previews()


def get_preview_default():
    return bpy.context.preferences.addons[__package__].preferences.preview_default


def copyCustomImage(filepath, filename):
    if os.path.exists(filepath):
        image_directory = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'custom_thumbnails'))
        destination_path = os.path.join(image_directory, filename)

        try:
            # create custom thumbnail folder if not existing
            if not os.path.exists(image_directory):
                os.makedirs(image_directory)

            import shutil
            shutil.copyfile(filepath, destination_path)
            return True
        except:
            pass
    return False


def removeCustomImage(filename):
    image_directory = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'custom_thumbnails'))
    destination_path = os.path.join(image_directory, filename)
    
    if os.path.isfile(destination_path):
        # make sure the image is only used once - else stop
        count = 0
        for v in readWidgets(JSON_USER_WIDGETS).values():
            if v.get("image") == filename:
                count += 1
            if count > 1:
                return False
            
        try:
            os.remove(destination_path)
            return True
        except:
            pass
    return False
