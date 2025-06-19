import bpy
import os
import json
import numpy
import re
from bpy.app.handlers import persistent
from .main_functions import get_preferences
from ..classes import BoneWidgetImportData, Widget, ColorSet
from .. import __package__

JSON_DEFAULT_WIDGETS = "widgets.json"
JSON_USER_WIDGETS = "user_widgets.json"
JSON_COLOR_PRESETS = "custom_color_sets.json"

widget_data = {}


def get_addon_dir():
    return os.path.dirname(__file__)


def get_custom_image_dir(image_folder):
    return os.path.abspath(os.path.join(get_addon_dir(), '..', image_folder))


def validate_json_data(data: dict, required_keys: tuple, can_be_empty: bool = True) -> bool:
    required_keys = set(required_keys)

    if not isinstance(data, dict):
        return False

    # Check if all required keys are present
    if not required_keys.issubset(data.keys()):
        return False

    if not can_be_empty:
        # Check if values are not empty
        if any(not data[key] for key in required_keys):
            return False
    return True


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
        custom_image_dir = get_custom_image_dir(image_folder)
        
        filename = os.path.basename(filepath)
        if not filename: filename = "widget_library.zip"
        elif not filename.endswith('.zip'): filename += ".zip"

        # start the zipping process
        try:
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
        except Exception as e:
            print("Error exporting widget library: ", e)
            return 0

    return len(wgts)
   

def import_widget_library(filepath, action=""):
    required_data_keys = ("vertices", "faces", "edges", "image") # json data
    wgts = {}

    from zipfile import ZipFile
    #dest_dir = os.path.abspath(os.path.join(get_addon_dir(), '..'))
    dest_dir = bpy.app.tempdir

    widget_import = BoneWidgetImportData()

    widget_import.import_type = "widget"

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

            # validate wgts data type
            if not isinstance(wgts, dict):
                raise TypeError(f"Expected a dictionary, but got {type(wgts).__name__}")
            
            current_wgts = read_widgets(JSON_USER_WIDGETS)

            # check for duplicate names
            for name, data in sorted(wgts.items()): # sorting by keys
                widget_import.total_num_imports += 1
                # validate json data
                if not validate_json_data(data, required_data_keys):
                    widget_import.failed_imports.append(Widget(name, data))
                    continue

                if action == "ASK":
                    widget_import.skipped_imports.append(Widget(name, data))
                elif action == "OVERWRITE":
                    widget_import.imported_items.append(Widget(name, data))
                elif action == "SKIP":
                    # check for duplicates
                    data_match = data == current_wgts[name]
                    if data_match:
                        widget_import.skipped_imports.append(Widget(name, data))
                        #widget_import.duplicate_imports.update({name : data})
                    elif name not in current_wgts:
                        widget_import.imported_items.append(Widget(name, data))
                    else:
                        widget_import.skipped_imports.append(Widget(name, data))
                else:
                    widget_import.failed_imports.append(Widget(name, data))

        except TypeError as e:  # Handle data type errors specifically
            print(f"Error while importing widget library: {e}")
            widget_import.json_import_error = True
        except Exception as e:
            print(f"Error while importing widget library: {e}")
            for name, data in wgts.items():
                widget_import.failed_imports.append(Widget(name, data))
                widget_import.total_num_imports = widget_import.failed()
    return widget_import


def update_widget_library(new_widgets: dict[str, dict[str, list | str]],
                          new_images: set[str], zip_filepath: str) -> None:
    current_widget = bpy.context.window_manager.widget_list  # store the currently selected widget

    wgts = read_widgets(JSON_USER_WIDGETS)
    wgts.update(new_widgets)
    
    write_widgets(wgts, JSON_USER_WIDGETS)

    # extract any images needed from zip library
    if new_images:
        from zipfile import ZipFile
        dest_dir = os.path.abspath(os.path.join(get_addon_dir(), '..'))
        if os.path.exists(zip_filepath):
            try:
                with ZipFile(zip_filepath, 'r') as zip_file:
                    for file in zip_file.namelist():
                        if file.startswith('custom_thumbnails/') and file.split("/")[1] in new_images:
                            zip_file.extract(file, dest_dir)
            except Exception as e:
                print("Failed to extract custom images: ", e)
        else:
            print("zip file path doesn't exist!! - ", zip_filepath)

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


################ COLOR PRESETS ################

def read_color_presets():
    presets = {}

    # Read the JSON file
    json_file = os.path.join(os.path.dirname(get_addon_dir()), JSON_COLOR_PRESETS)
    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            presets = json.load(file)
    
    presets = {item["name"]: item for item in presets} # convert to dictionary

    return presets


def update_color_presets(new_presets, zip_filepath):
    for preset in new_presets:
        add_color_set(bpy.context, preset)

    # extract any images needed from zip library
    # if new_images:
    #     from zipfile import ZipFile
    #     dest_dir = os.path.abspath(os.path.join(get_addon_dir(), '..'))
    #     if os.path.exists(zip_filepath):
    #         try:
    #             with ZipFile(zip_filepath, 'r') as zip_file:
    #                 for file in zip_file.namelist():
    #                     if file.startswith('custom_thumbnails/') and file.split("/")[1] in new_images:
    #                         zip_file.extract(file, dest_dir)
    #         except:
    #             pass


def import_color_presets(filepath, action=""):
    required_data_keys = ("name", "normal", "select", "active") # json data
    presets = None

    from zipfile import ZipFile
    dest_dir = os.path.abspath(os.path.join(get_addon_dir(), '..'))

    presets_import = BoneWidgetImportData()

    presets_import.import_type = "colorset"

    if os.path.exists(filepath) and action:
        try:
            with ZipFile(filepath, 'r') as zip_file:
                # extract images
                for file in zip_file.namelist():
                    #if file.startswith('preset_thumbnails/'):
                        #zip_file.extract(file, dest_dir)
                    if file.endswith('.json'): # extract data from the .json file
                        f = zip_file.read(file)
                        json_data = f.decode('utf8').replace("'", '"')
                        presets = json.loads(json_data)

            # validate presets data type
            if not isinstance(presets, list):
                raise TypeError(f"Expected a list, but got {type(presets).__name__}")
            
            current_presets = read_color_presets()

            # check for duplicate presets
            for preset in presets:
                presets_import.total_num_imports += 1

                # validate json data
                if not validate_json_data(preset, required_data_keys, False):
                    presets_import.failed_imports.append(ColorSet(preset))
                    continue

                name = preset['name']
                if action == "ASK":
                    presets_import.skipped_imports.append(ColorSet(preset))
                elif action == "OVERWRITE":
                    presets_import.imported_items.append(ColorSet(preset))
                elif action == "SKIP":
                    # name and colors match or just colors match
                    if colors_match(preset, current_presets[name]):
                        presets_import.skipped_imports.append(ColorSet(preset))
                    elif not name in current_presets:
                        presets_import.imported_items.append(ColorSet(preset))
                    else:
                        presets_import.skipped_imports.append(ColorSet(preset))
                else:
                    presets_import.failed_imports.append(ColorSet(preset))


        except TypeError as e:  # Handle data type errors specifically
                print(f"Error while importing color presets: {e}")
                presets_import.json_import_error = True
        except Exception as e:
            print(f"Error while importing color presets: {e}")
            for preset in presets:
                presets_import.failed_imports.append(ColorSet(preset))
                presets_import.total_num_imports = presets_import.failed()              
    return presets_import


def colors_match(set1, set2):
    if isinstance(set1, dict):
        return set1['normal'] == set2['normal'] \
                and set1['select'] == set2['select'] \
                and set1['active'] == set2['active']
    elif isinstance(set1, bpy.types.ThemeBoneColorSet):
        return set1.normal == set2.normal \
                and set1.select == set2.select \
                and set1.active == set2.active


def scan_armature_color_presets(context, armature):
    found_color_sets = set()

    colorsets_import = BoneWidgetImportData()
    colorsets_import.import_type = "colorset"

    current_color_sets = context.window_manager.custom_color_presets

    # edit bones
    for bone in armature.bones:
        if bone.color.is_custom:
            is_unique_colorset = True
            for color_set in current_color_sets:
                if colors_match(bone.color.custom, color_set):
                    is_unique_colorset = False  # not unique
                    break

            color_data = (tuple(bone.color.custom.normal), tuple(bone.color.custom.select), tuple(bone.color.custom.active))
            if is_unique_colorset and not color_data in found_color_sets:
                color_set = {attr: list(getattr(bone.color.custom, attr)[:3]) for attr in ["normal", "active", "select"]}
                color_set['name'] = bone.name
                colorsets_import.skipped_imports.append(ColorSet(color_set))
                found_color_sets.add(color_data)

        # pose bones
        pose_bone = context.object.pose.bones.get(bone.name)
        if pose_bone.color.is_custom:
            is_unique_colorset = True
            for color_set in current_color_sets:
                if colors_match(pose_bone.color.custom, color_set):
                    is_unique_colorset = False # not unique
                    break
            
            color_data = (tuple(pose_bone.color.custom.normal), tuple(pose_bone.color.custom.select), tuple(pose_bone.color.custom.active))
            if is_unique_colorset and not color_data in found_color_sets:
                color_set = {attr: list(getattr(pose_bone.color.custom, attr)[:3]) for attr in ["normal", "active", "select"]}
                color_set['name'] = bone.name
                colorsets_import.skipped_imports.append(ColorSet(color_set))
                found_color_sets.add(color_data)

    return colorsets_import


def export_color_presets(filepath, context):
    color_presets = len(context.window_manager.custom_color_presets)

    if color_presets:
        dest_dir = os.path.dirname(filepath)
        json_dir = os.path.dirname(get_addon_dir())
        #image_folder = 'preset_thumbnails'
        #custom_image_dir = get_custom_image_dir(image_folder)
        
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


def add_color_set_from_bone(context, bone, suffix_name):
    new_item = context.window_manager.custom_color_presets.add()

    color_set = bone.color.custom

    new_name = bone.name + suffix_name  # CHANGE LATER

    # check if the name already ends with an incremented number
    match = re.match(r"^(.*)\.(\d{3})$", new_name)
    count = int(match.group(2)) if match else 1
    base_name = match.group(1) if match else new_name

    while any(item.name == new_name for item in context.window_manager.custom_color_presets):
        new_name = f"{base_name}.{count:03d}"
        count += 1

    new_item.name = new_name

    if not color_set: # new default color set
        new_item.normal = (1.0, 0.0, 0.0)
        new_item.select = (0.0, 1.0, 0.0)
        new_item.active = (0.0, 0.0, 1.0)
    else:
        new_item.normal = color_set.normal
        new_item.select = color_set.select
        new_item.active = color_set.active


def add_color_set(context, color_set = None):
    new_item = context.window_manager.custom_color_presets.add()

    base_name = "Color Set" if not color_set else color_set.name
    new_name = base_name

    # check if the name already ends with an incremented number
    match = re.match(r"^(.*)\.(\d{3})$", base_name)
    count = int(match.group(2)) if match else 1
    base_name = match.group(1) if match else new_name

    while any(item.name == new_name for item in context.window_manager.custom_color_presets):
        new_name = f"{base_name}.{count:03d}"
        count += 1

    new_item.name = new_name

    if not color_set: # new default color set
        new_item.normal = (1.0, 0.0, 0.0)
        new_item.select = (0.0, 1.0, 0.0)
        new_item.active = (0.0, 0.0, 1.0)
    else:
        new_item.normal = color_set.normal
        new_item.select = color_set.select
        new_item.active = color_set.active


def save_color_sets(context):
    if not bpy.context.scene.turn_off_colorset_save:
        bpy.context.scene.turn_off_colorset_save = True
        color_sets = [{
            "name": item.name,
            "normal": list(item.normal),
            "select": list(item.select),
            "active": list(item.active)
        } for item in context.window_manager.custom_color_presets]

        filepath = os.path.join(get_addon_dir(), '..', JSON_COLOR_PRESETS)
        with open(filepath, 'w') as f:
            json.dump(color_sets, f, indent=4)
        bpy.context.scene.turn_off_colorset_save = False


@persistent
def load_color_presets(_):
    filepath = os.path.join(get_addon_dir(), '..', JSON_COLOR_PRESETS)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            color_sets = json.load(f)
            bpy.context.window_manager.custom_color_presets.clear() # TEST
            bpy.context.scene.turn_off_colorset_save = True
            for item in color_sets:
                new_item = bpy.context.window_manager.custom_color_presets.add()
                new_item.name = item["name"]
                new_item.normal = item["normal"]
                new_item.select = item["select"]
                new_item.active = item["active"]
            bpy.context.scene.turn_off_colorset_save = False
