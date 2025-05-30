import bpy
import os
import json
import numpy
from bpy.app.handlers import persistent
from .main_functions import get_preferences
from .. import __package__

JSON_DEFAULT_WIDGETS = "widgets.json"
JSON_USER_WIDGETS = "user_widgets.json"
JSON_COLOR_PRESETS = "custom_color_sets.json"

widget_data = {}


def objectDataToDico(object, custom_image):
    verts = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = object.evaluated_get(depsgraph).to_mesh()
    for v in mesh.vertices:
        verts.append(tuple(numpy.array(tuple(v.co)) *
                           (object.scale[0], object.scale[1], object.scale[2])))

    polygons = []
    for p in mesh.polygons:
        polygons.append(tuple(p.vertices))

    edges = []
    for e in mesh.edges:
        edges.append(e.key)

    custom_image = custom_image if custom_image != "" else "user_defined.png"

    wgts = {"vertices": verts, "edges": edges, "faces": polygons, "image": custom_image}

    return(wgts)


def read_widgets(filename = ""):
    global widget_data
    wgts = {}

    if not filename:
        files = [JSON_DEFAULT_WIDGETS, JSON_USER_WIDGETS]
    else:
        files = [filename]

    for file in files:
        jsonFile = os.path.join(os.path.dirname(get_addon_dir()), file)
        if os.path.exists(jsonFile):
            f = open(jsonFile, 'r')
            wgts.update(json.load(f))
            f.close()
            
    if not filename: # if both files have been read
        widget_data = wgts.copy()

    return (wgts)


def get_widget_data(widget):
    return widget_data[widget]


def write_widgets(wgts, file):
    jsonFile = os.path.join(os.path.dirname(get_addon_dir()), file)
    #if os.path.exists(jsonFile):
    f = open(jsonFile, 'w')
    f.write(json.dumps(wgts))
    f.close()


def add_remove_widgets(context, addOrRemove, items, widgets, widget_name="", custom_image=""):
    wgts = {}

    # file from where the widget should be read or written to
    file = JSON_USER_WIDGETS

    widget_items = []
    for widget_item in items:
        widget_items.append(widget_item[1])

    activeShape = None
    ob_name = None
    return_message = ""
    if addOrRemove == 'add':
        wgts = read_widgets(file)
        bw_widget_prefix = get_preferences(context).widget_prefix
        for ob in widgets:
            if not widget_name:
                if ob.name.startswith(bw_widget_prefix):
                    ob_name = ob.name[len(bw_widget_prefix):]
                else:
                    ob_name = ob.name
            else:
                ob_name = widget_name

            if (ob_name) not in widget_items:
                widget_items.append(ob_name)
                wgts[ob_name] = objectDataToDico(ob, custom_image)
                activeShape = ob_name
                return_message = "Widget - " + ob_name + " has been added!"

    elif addOrRemove == 'remove':
        user_widgets = read_widgets(file)
        if widgets in user_widgets:
            wgts = user_widgets
        else:
            file = JSON_DEFAULT_WIDGETS
            wgts = read_widgets(file)
        
        del wgts[widgets]
        if widgets in widget_items:
            widget_index = widget_items.index(widgets)
            activeShape = widget_items[widget_index + 1] if widget_index == 0 else widget_items[widget_index - 1]
            widget_items.remove(widgets)
        return_message = "Widget - " + widgets + " has been removed!"

    if activeShape is not None:

        write_widgets(wgts, file)

        # to handle circular import error
        from .functions import create_preview_collection

        create_preview_collection()
    
        # trigger an update and display widget
        bpy.context.window_manager.widget_list = activeShape

        return 'INFO', return_message
    elif ob_name is not None:
        return 'WARNING', "Widget - " + ob_name + " already exists!"


def export_widget_library(filepath):
    wgts = read_widgets(JSON_USER_WIDGETS)

    if wgts:
        # variables needed for exporting widgets
        dest_dir = os.path.dirname(filepath)
        json_dir = os.path.dirname(get_addon_dir())
        image_folder = 'custom_thumbnails'
        custom_image_dir = os.path.abspath(os.path.join(get_addon_dir(), '..', image_folder))
        
        filename = os.path.basename(filepath)
        if not filename: filename = "widget_library.zip"
        elif not filename.endswith('.zip'): filename += ".zip"

        # start the zipping process
        from zipfile import ZipFile
        with ZipFile(os.path.join(dest_dir, filename), "w") as zip:
            # write the json file
            file = os.path.join(json_dir, JSON_USER_WIDGETS)
            arcname = os.path.basename(file)
            zip.write(file, arcname=arcname)

            # write the custom images if present
            if os.path.exists(custom_image_dir):
                from pathlib import Path
                for filepath in Path(custom_image_dir).iterdir():
                    arcname = os.path.join(image_folder, os.path.basename(filepath))
                    zip.write(filepath, arcname=arcname)

    return len(wgts)


def export_color_presets(filepath, context):
    color_presets = len(context.window_manager.custom_color_presets)

    if color_presets:
        # variables needed for exporting widgets
        dest_dir = os.path.dirname(filepath)
        json_dir = os.path.dirname(get_addon_dir())
        #image_folder = 'preset_thumbnails'
        #custom_image_dir = os.path.abspath(os.path.join(get_addon_dir(), '..', image_folder))
        
        filename = os.path.basename(filepath)
        if not filename: filename = "color_presets.zip"
        elif not filename.endswith('.zip'): filename += ".zip"

        # start the zipping process
        try:
            from zipfile import ZipFile
            with ZipFile(os.path.join(dest_dir, filename), "w") as zip:
                # write the json file
                file = os.path.join(json_dir, JSON_COLOR_PRESETS)
                arcname = os.path.basename(file)
                zip.write(file, arcname=arcname)
        except Exception as e:
            print("Error exporting color presets: ", e)
            return 0

    return color_presets


class WidgetImportStats:
    def __init__(self):
        self.new_widgets = 0
        self.failed_widgets = {}
        self.skipped_widgets = [] # to make sure the data won't change order
        self.widgets = {}
    
    def skipped(self):
        return len(self.skipped_widgets)
    
    def failed(self):
        return len(self.failed_widgets)


def import_widget_library(filepath, action=""):
    wgts = {}

    from zipfile import ZipFile
    dest_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

    widget_import = WidgetImportStats()

    if os.path.exists(filepath) and action:
        try:
            with ZipFile(filepath, 'r') as zip_file:
                # extract images
                for file in zip_file.namelist():
                    if file.startswith('custom_thumbnails/'):
                        zip_file.extract(file, dest_dir)
                    elif file.endswith('.json'): # extract data from the .json file
                        f = zip_file.read(file)
                        json_data = f.decode('utf8').replace("'", '"')
                        wgts = json.loads(json_data)

            current_wgts = read_widgets(JSON_USER_WIDGETS)

            # check for duplicate names
            for name, data in sorted(wgts.items()): # sorting by keys
                if action == "ASK":
                    widget_import.skipped_widgets.append({name : data})
                elif action == "OVERWRITE":
                    widget_import.widgets.update({name : data})
                    widget_import.new_widgets += 1
                elif action == "SKIP":
                    if not name in current_wgts:
                        widget_import.widgets.update({name : data})
                        widget_import.new_widgets += 1
                    else:
                        widget_import.skipped_widgets.append({name : data})
                else:
                    widget_import.failed_widgets.update({name : data})

        except Exception as e:
            print(f"Error while importing widget library: {e}")
    return widget_import


def update_widget_library(new_widgets, new_images, zip_filepath):
    current_widget = bpy.context.window_manager.widget_list
    wgts = read_widgets(JSON_USER_WIDGETS)

    wgts.update(new_widgets)
    
    write_widgets(wgts, JSON_USER_WIDGETS)

    # extract any images needed from zip library
    if new_images:
        from zipfile import ZipFile
        dest_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
        if os.path.exists(zip_filepath):
            try:
                with ZipFile(zip_filepath, 'r') as zip_file:
                    for file in zip_file.namelist():
                        if file.startswith('custom_thumbnails/') and file.split("/")[1] in new_images:
                            zip_file.extract(file, dest_dir)
            except:
                pass

    # update the preview panel
    from .functions import create_preview_collection
    create_preview_collection()
    
    # trigger an update and display original but updated widget
    bpy.context.window_manager.widget_list = current_widget


def update_custom_image(image_name):
    current_widget = bpy.context.window_manager.widget_list
    current_widget_data = get_widget_data(current_widget)

    # swap out the image
    current_widget_data['image'] = image_name

     # update and write the new data
    wgts = read_widgets(JSON_USER_WIDGETS)
    if current_widget in wgts:
        wgts[current_widget] = current_widget_data
        write_widgets(wgts, JSON_USER_WIDGETS)
    else:
        wgts = read_widgets(JSON_DEFAULT_WIDGETS)
        wgts[current_widget] = current_widget_data
        write_widgets(wgts, JSON_DEFAULT_WIDGETS)

    # update the preview panel
    from .functions import create_preview_collection
    create_preview_collection()
    
    # trigger an update and display original but updated widget
    bpy.context.window_manager.widget_list = current_widget


def reset_default_images():
    current_widget = bpy.context.window_manager.widget_list
    wgts = read_widgets(JSON_DEFAULT_WIDGETS)

    for name, data in wgts.items():
        image = f"{name}.png"
        data["image"] = image
    
    write_widgets(wgts, JSON_DEFAULT_WIDGETS)

    # update the preview panel
    from .functions import create_preview_collection
    create_preview_collection()
    
    # trigger an update and display original but updated widget
    bpy.context.window_manager.widget_list = current_widget


def get_addon_dir():
    return os.path.dirname(__file__)


def save_color_sets(context):
    if not bpy.context.scene.turn_off_colorset_save:
        bpy.context.scene.turn_off_colorset_save = True
        color_sets = [{
            "name": item.name,
            "normal": list(item.normal),
            "select": list(item.select),
            "active": list(item.active)
        } for item in context.window_manager.custom_color_presets]

        filepath = os.path.join(get_addon_dir(), '..', "custom_color_sets.json")
        with open(filepath, 'w') as f:
            json.dump(color_sets, f, indent=4)
        bpy.context.scene.turn_off_colorset_save = False


@persistent
def load_color_presets(_):
    filepath = os.path.join(get_addon_dir(), '..', "custom_color_sets.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            color_sets = json.load(f)
            for item in color_sets:
                bpy.context.scene.turn_off_colorset_save = True
                new_item = bpy.context.window_manager.custom_color_presets.add()
                new_item.name = item["name"]
                new_item.normal = item["normal"]
                new_item.select = item["select"]
                new_item.active = item["active"]
                bpy.context.scene.turn_off_colorset_save = False

