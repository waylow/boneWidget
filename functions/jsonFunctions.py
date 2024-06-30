import bpy
import os
import json
import numpy
from .. import __package__

JSON_DEFAULT_WIDGETS = "widgets.json"
JSON_USER_WIDGETS = "user_widgets.json"


def objectDataToDico(object):
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

    wgts = {"vertices": verts, "edges": edges, "faces": polygons, "image": "user_defined.png"}

    return(wgts)


def readWidgets(file = ""):
    wgts = {}

    if not file:
        files = [JSON_DEFAULT_WIDGETS, JSON_USER_WIDGETS]
    else:
        files = [file]

    for file in files:
        jsonFile = os.path.join(os.path.dirname(os.path.dirname(__file__)), file)
        if os.path.exists(jsonFile):
            f = open(jsonFile, 'r')
            wgts.update(json.load(f))
            f.close()

    return (wgts)


def writeWidgets(wgts, file):
    jsonFile = os.path.join(os.path.dirname(os.path.dirname(__file__)), file)
    #if os.path.exists(jsonFile):
    f = open(jsonFile, 'w')
    f.write(json.dumps(wgts))
    f.close()


def addRemoveWidgets(context, addOrRemove, items, widgets, widget_name=""):
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
                wgts[ob_name] = objectDataToDico(ob)
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
        if not filepath.endswith(".bwl"):
            filename += ".bwl"
        f = open(os.path.join(filepath), 'w')
        f.write(json.dumps(wgts))
        f.close()

    return len(wgts)


def importWidgetLibrary(filepath):
    wgts = {}
    num_new_widgets = 0
    failed_imports = []

    if os.path.exists(filepath):
        try:
            f = open(filepath, 'r')
            wgts = json.load(f)
            f.close()

            current_wgts = readWidgets(JSON_USER_WIDGETS)

            # check for duplicate names
            for name, data in wgts.items():
                if name not in current_wgts:
                    current_wgts.update({name : data})
                    num_new_widgets += 1
                else:
                    failed_imports.append(name)

            # if there are new widgets
            if num_new_widgets:
                writeWidgets(current_wgts, JSON_USER_WIDGETS)
        except:
            pass

    return num_new_widgets, failed_imports
