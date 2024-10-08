import bpy
import os
import json
import numpy
from .. import __package__

JSON_DEFAULT_WIDGETS = "widgets.json"
JSON_USER_WIDGETS = "user_widgets.json"

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


def readWidgets(filename = ""):
    global widget_data
    wgts = {}

    if not filename:
        files = [JSON_DEFAULT_WIDGETS, JSON_USER_WIDGETS]
    else:
        files = [filename]

    for file in files:
        jsonFile = os.path.join(os.path.dirname(os.path.dirname(__file__)), file)
        if os.path.exists(jsonFile):
            f = open(jsonFile, 'r')
            wgts.update(json.load(f))
            f.close()
            
    if not filename: # if both files have been read
        widget_data = wgts.copy()

    return (wgts)


def getWidgetData(widget):
    return widget_data[widget]


def writeWidgets(wgts, file):
    jsonFile = os.path.join(os.path.dirname(os.path.dirname(__file__)), file)
    #if os.path.exists(jsonFile):
    f = open(jsonFile, 'w')
    f.write(json.dumps(wgts))
    f.close()


def addRemoveWidgets(context, addOrRemove, items, widgets, widget_name="", custom_image=""):
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
        wgts = readWidgets(file)
        bw_widget_prefix = bpy.context.preferences.addons[__package__].preferences.widget_prefix
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
        user_widgets = readWidgets(file)
        if widgets in user_widgets:
            wgts = user_widgets
        else:
            file = JSON_DEFAULT_WIDGETS
            wgts = readWidgets(file)
        
        del wgts[widgets]
        if widgets in widget_items:
            widget_index = widget_items.index(widgets)
            activeShape = widget_items[widget_index + 1] if widget_index == 0 else widget_items[widget_index - 1]
            widget_items.remove(widgets)
        return_message = "Widget - " + widgets + " has been removed!"

    if activeShape is not None:

        writeWidgets(wgts, file)

        # to handle circular import error
        from .functions import createPreviewCollection

        createPreviewCollection()
    
        # trigger an update and display widget
        bpy.context.window_manager.widget_list = activeShape

        return 'INFO', return_message
    elif ob_name is not None:
        return 'WARNING', "Widget - " + ob_name + " already exists!"


def exportWidgetLibrary(filepath):
    wgts = readWidgets(JSON_USER_WIDGETS)

    if wgts:
        # variables needed for exporting widgets
        dest_dir = os.path.dirname(filepath)
        json_dir = os.path.dirname(os.path.dirname(__file__))
        image_folder = 'custom_thumbnails'
        custom_image_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', image_folder))
        
        filename = os.path.basename(filepath)
        if not filename: filename = "widgetLibrary.zip"
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


def importWidgetLibrary(filepath, action=""):
    wgts = {}

    from zipfile import ZipFile
    dest_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

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

            current_wgts = readWidgets(JSON_USER_WIDGETS)

            widgetImport = WidgetImportStats()

            # check for duplicate names
            for name, data in sorted(wgts.items()): # sorting by keys
                if action == "ASK":
                    widgetImport.skipped_widgets.append({name : data})
                elif action == "OVERWRITE":
                    widgetImport.widgets.update({name : data})
                    widgetImport.new_widgets += 1
                elif action == "SKIP":
                    if not name in current_wgts:
                        widgetImport.widgets.update({name : data})
                        widgetImport.new_widgets += 1
                    else:
                        widgetImport.skipped_widgets.append({name : data})
                else:
                    widgetImport.failed_widgets.update({name : data})

        except:
            pass
    return widgetImport


def updateWidgetLibrary(new_widgets, new_images, zip_filepath):
    current_widget = bpy.context.window_manager.widget_list
    wgts = readWidgets(JSON_USER_WIDGETS)

    wgts.update(new_widgets)
    
    writeWidgets(wgts, JSON_USER_WIDGETS)

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
    from .functions import createPreviewCollection
    createPreviewCollection()
    
    # trigger an update and display original but updated widget
    bpy.context.window_manager.widget_list = current_widget


def updateCustomImage(image_name):
    current_widget = bpy.context.window_manager.widget_list
    current_widget_data = getWidgetData(current_widget)

    # swap out the image
    current_widget_data['image'] = image_name

     # update and write the new data
    wgts = readWidgets(JSON_USER_WIDGETS)
    if current_widget in wgts:
        wgts[current_widget] = current_widget_data
        writeWidgets(wgts, JSON_USER_WIDGETS)
    else:
        wgts = readWidgets(JSON_DEFAULT_WIDGETS)
        wgts[current_widget] = current_widget_data
        writeWidgets(wgts, JSON_DEFAULT_WIDGETS)

    # update the preview panel
    from .functions import createPreviewCollection
    createPreviewCollection()
    
    # trigger an update and display original but updated widget
    bpy.context.window_manager.widget_list = current_widget


def resetDefaultImages():
    current_widget = bpy.context.window_manager.widget_list
    wgts = readWidgets(JSON_DEFAULT_WIDGETS)

    for name, data in wgts.items():
        image = f"{name}.png"
        data["image"] = image
    
    writeWidgets(wgts, JSON_DEFAULT_WIDGETS)

    # update the preview panel
    from .functions import createPreviewCollection
    createPreviewCollection()
    
    # trigger an update and display original but updated widget
    bpy.context.window_manager.widget_list = current_widget
