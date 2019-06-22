import bpy
import os
import json
import numpy


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

    wgts = {"vertices": verts, "edges": edges, "faces": polygons}
    # print(wgts)
    return(wgts)


def readWidgets():
    wgts = {}

    jsonFile = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'widgets.json')
    if os.path.exists(jsonFile):
        f = open(jsonFile, 'r')
        wgts = json.load(f)

    return (wgts)


def addRemoveWidgets(context, addOrRemove, items, widgets):
    wgts = readWidgets()

    widget_items = []
    for widget_item in items:
        widget_items.append(widget_item[1])

    if addOrRemove == 'add':
        bw_widget_prefix = bpy.context.preferences.addons["boneWidget"].preferences.widget_prefix
        for ob in widgets:
            if ob.name.startswith(bw_widget_prefix):
                ob_name = ob.name[len(bw_widget_prefix):]
            else:
                ob_name = ob.name
            wgts[ob_name] = objectDataToDico(ob)
            if (ob_name) not in widget_items:
                widget_items.append(ob_name)

    elif addOrRemove == 'remove':
        del wgts[widgets]
        widget_items.remove(widgets)

    del bpy.types.Scene.widget_list

    widget_itemsSorted = []
    for w in sorted(widget_items):
        widget_itemsSorted.append((w, w, ""))

    bpy.types.Scene.widget_list = bpy.props.EnumProperty(items=widget_itemsSorted)

    jsonFile = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'widgets.json')
    if os.path.exists(jsonFile):
        f = open(jsonFile, 'w')
        f.write(json.dumps(wgts))
        f.close()
