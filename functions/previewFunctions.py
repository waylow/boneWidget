import bpy
import bpy.utils.previews
from .jsonFunctions import readWidgets, getWidgetData, get_addon_dir, JSON_USER_WIDGETS
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
    directory = os.path.abspath(os.path.join(get_addon_dir(), '..', 'thumbnails'))
    custom_directory = os.path.abspath(os.path.join(get_addon_dir(), '..', 'custom_thumbnails'))

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
        image_directory = os.path.abspath(os.path.join(get_addon_dir(), '..', 'custom_thumbnails'))
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
    image_directory = os.path.abspath(os.path.join(get_addon_dir(), '..', 'custom_thumbnails'))
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


####   Auto Thumbnail Functions ####
def create_wireframe_copy(obj, use_color, color, thickness):
    copy = obj.copy()
    copy.data = obj.data.copy()
    if not use_color:
        copy.color = color

    wire_mod = copy.modifiers.new(name="BONEWIDGET_Wireframe", type='WIREFRAME')
    wire_mod.use_replace = True
    wire_mod.thickness = thickness

    return copy

def setup_viewport(context, auto_frame):
    area = context.area
    space = context.space_data

    if area.type != 'VIEW_3D' or space.type != 'VIEW_3D':
        raise RuntimeError("Operator must be run from a 3D Viewport")

    region_3d = space.region_3d
    original_view_matrix = region_3d.view_matrix.copy()

    # Prepare viewport for clean render
    space.overlay.show_overlays = False
    space.shading.type = 'SOLID'
    space.shading.light = 'FLAT'
    space.shading.color_type = 'OBJECT'

    if auto_frame:
        bpy.ops.view3d.view_selected()

    return original_view_matrix

def get_viewport_shading(context):
    """Returns the shading settings for all 3D Viewport areas."""
    viewports = []
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    viewports.append({
                        "area": area,
                        "space": space,
                        "show_overlays": space.overlay.show_overlays,
                        "shading_settings": {
                            "type": space.shading.type,
                            "light": space.shading.light,
                            "color_type": space.shading.color_type,
                            }
                    })
                    
    return viewports

def restore_viewport_position(context, view_matrix):
    if context.space_data.type == 'VIEW_3D':
        context.space_data.region_3d.view_matrix = view_matrix


def restore_viewport_shading(viewports):
    """Restores previously saved shading settings."""
    for vp in viewports:
        space = vp["space"]
        for attr, value in vp["shading_settings"].items():
            setattr(space.shading, attr, value)


def render_widget_thumbnail(filepath, resolution):
    image_directory = os.path.abspath(os.path.join(get_addon_dir(), '..', 'custom_thumbnails'))
    destination_path = os.path.join(image_directory, 'test.png')

    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.view_settings.view_transform = 'Standard'
    scene.render.film_transparent = True

    bpy.ops.render.opengl(write_still=False, view_context=True)
    bpy.data.images['Render Result'].save_render(filepath=bpy.path.abspath(destination_path))
    print("File path:", bpy.path.abspath(destination_path))

# def removeCustomImage(filename):
#     image_directory = os.path.abspath(os.path.join(get_addon_dir(), '..', 'custom_thumbnails'))
#     destination_path = os.path.join(image_directory, filename)
    
#     if os.path.isfile(destination_path):
#         # make sure the image is only used once - else stop
#         count = 0
#         for v in readWidgets(JSON_USER_WIDGETS).values():
#             if v.get("image") == filename:
#                 count += 1
#             if count > 1:
#                 return False
            
#         try:
#             os.remove(destination_path)
#             return True
#         except:
#             pass
#     return False