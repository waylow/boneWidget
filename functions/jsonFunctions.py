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
        if len(polygons) != 0:
            for vert_indices in polygons:
                if e.key[0] and e.key[1] not in vert_indices:
                    edges.append(e.key)
        else:
            edges.append(e.key)

    wgts = {"vertices": verts, "edges": edges, "faces": polygons, "image": "user_defined.png"}
    # print(wgts)
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
        widget_items.remove(widgets)
        activeShape = widget_items[0]
        return_message = "Widget - " + widgets + " has been removed!"

    if activeShape is not None:
        del bpy.types.Scene.widget_list

        widget_itemsSorted = []
        for w in sorted(widget_items):
            widget_itemsSorted.append((w, w, ""))

        bpy.types.Scene.widget_list = bpy.props.EnumProperty(
            items=widget_itemsSorted, name="Shape", description="Shape")
        bpy.context.scene.widget_list = activeShape
        writeWidgets(wgts, file)

        # trigger an update and display widget
        bpy.context.window_manager.widget_list = bpy.context.window_manager.widget_list
        bpy.context.window_manager.widget_list = activeShape

        return 'INFO', return_message
    elif ob_name is not None:
        return 'WARNING', "Widget - " + ob_name + " already exists!"
