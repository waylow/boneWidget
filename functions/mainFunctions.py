import bpy
import numpy
from .jsonFunctions import objectDataToDico


def get_collection(context):
    bw_collection_name = context.preferences.addons["boneWidget"].preferences.bonewidget_collection_name
    collection = context.scene.collection.children.get(bw_collection_name)
    if collection:
        return collection
    collection = bpy.data.collections.get(bw_collection_name)
    if not collection:
        collection = bpy.data.collections.new(bw_collection_name)
    context.scene.collection.children.link(collection)
    return collection


def boneMatrix(widget, matchBone):
    widget.matrix_local = matchBone.bone.matrix_local
    # need to make this take the armature scale into account
    # id_data below now points to the armature data rather than the object
    # widget.matrix_world = bpy.context.active_pose_bone.id_data.matrix_world @ matchBone.bone.matrix_local
    # widget.matrix_world = matchBone.matrix_world @ matchBone.bone.matrix_local
    widget.scale = [matchBone.bone.length, matchBone.bone.length, matchBone.bone.length]
    widget.data.update()


def fromWidgetFindBone(widget):
    matchBone = None
    for ob in bpy.context.scene.objects:
        if ob.type == "ARMATURE":
            for bone in ob.pose.bones:
                if bone.custom_shape == widget:
                    matchBone = bone

    return matchBone


def createWidget(bone, widget, relative, size, scale, slide, collection):
    C = bpy.context
    D = bpy.data
    bw_widget_prefix = C.preferences.addons["boneWidget"].preferences.widget_prefix

    if bone.custom_shape_transform:
        matrixBone = bone.custom_shape_transform
    else:
        matrixBone = bone

    if bone.custom_shape:
        bone.custom_shape.name = bone.custom_shape.name+"_old"
        bone.custom_shape.data.name = bone.custom_shape.data.name+"_old"
        if C.scene.collection.objects.get(bone.custom_shape.name):
            C.scene.collection.objects.unlink(bone.custom_shape)

    # make the data name include the prefix
    newData = D.meshes.new(bw_widget_prefix + bone.name)

    if relative == True:
        boneLength = 1
    else:
        boneLength = (1/bone.bone.length)

    newData.from_pydata(numpy.array(widget['vertices'])*[size*scale[0]*boneLength, size*scale[2]
                                                         * boneLength, size*scale[1]*boneLength]+[0, slide, 0], widget['edges'], widget['faces'])
    newData.update(calc_edges=True)

    newObject = D.objects.new(bw_widget_prefix + bone.name, newData)

    newObject.data = newData
    newObject.name = bw_widget_prefix + bone.name
    # C.scene.collection.objects.link(newObject)
    collection.objects.link(newObject)
    # When it creates the widget it still doesn't take the armature scale into account
    newObject.matrix_world = matrixBone.bone.matrix_local
    newObject.scale = [matrixBone.bone.length, matrixBone.bone.length, matrixBone.bone.length]
    layer = bpy.context.view_layer
    layer.update()

    bone.custom_shape = newObject
    bone.bone.show_wire = True


def symmetrizeWidget(bone, collection):
    C = bpy.context
    D = bpy.data
    bw_widget_prefix = C.preferences.addons["boneWidget"].preferences.widget_prefix

    widget = bone.custom_shape

    if findMirrorObject(bone).custom_shape_transform:
        mirrorBone = findMirrorObject(bone).custom_shape_transform
    else:
        mirrorBone = findMirrorObject(bone)

    mirrorWidget = mirrorBone.custom_shape

    if mirrorWidget:
        mirrorWidget.name = mirrorWidget.name+"_old"
        mirrorWidget.data.name = mirrorWidget.data.name+"_old"
        # don't unlink
        '''
        if C.scene.objects.get(mirrorWidget.name):
            C.scene.objects.unlink(mirrorWidget)
        '''
    newData = widget.data.copy()
    for vert in newData.vertices:
        vert.co = numpy.array(vert.co)*(-1, 1, 1)

    newObject = widget.copy()
    newObject.data = newData
    newData.update()
    newObject.name = bw_widget_prefix + mirrorBone.name
    collection.objects.link(newObject)
    # C.scene.objects.link(newObject)
    newObject.matrix_local = mirrorBone.bone.matrix_local
    newObject.scale = [mirrorBone.bone.length, mirrorBone.bone.length, mirrorBone.bone.length]

    layer = bpy.context.view_layer
    layer.update()

    mirrorBone.custom_shape = newObject
    mirrorBone.bone.show_wire = True


def editWidget(active_bone):
    C = bpy.context
    D = bpy.data
    widget = active_bone.custom_shape

    armature = active_bone.id_data
    bpy.ops.object.mode_set(mode='OBJECT')
    C.active_object.select_set(False)

    '''
    if C.space_data.lock_camera_and_layers == False :
        visibleLayers = numpy.array(bpy.context.space_data.layers)+widget.layers-armature.layers
        bpy.context.space_data.layers = visibleLayers.tolist()

    else :
        visibleLayers = numpy.array(bpy.context.scene.layers)+widget.layers-armature.layers
        bpy.context.scene.layers = visibleLayers.tolist()
    '''
    collection = get_collection(C)
    collection.hide_viewport = False
    if C.space_data.local_view:
        bpy.ops.view3d.localview()

    # select object and make it active
    widget.select_set(True)
    bpy.context.view_layer.objects.active = widget
    bpy.ops.object.mode_set(mode='EDIT')


def returnToArmature(widget):
    C = bpy.context
    D = bpy.data

    bone = fromWidgetFindBone(widget)
    armature = bone.id_data

    if C.active_object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')

    '''
    if C.space_data.lock_camera_and_layers == False :
        visibleLayers = numpy.array(bpy.context.space_data.layers)-widget.layers+armature.layers
        bpy.context.space_data.layers = visibleLayers.tolist()

    else :
        visibleLayers = numpy.array(bpy.context.scene.layers)-widget.layers+armature.layers
        bpy.context.scene.layers = visibleLayers.tolist()
    '''
    collection = get_collection(C)
    collection.hide_viewport = True
    if C.space_data.local_view:
        bpy.ops.view3d.localview()
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    armature.data.bones[bone.name].select = True
    armature.data.bones.active = armature.data.bones[bone.name]


def findMirrorObject(object):
    if object.name.endswith("L"):
        suffix = 'R'
    elif object.name.endswith("R"):
        suffix = 'L'
    elif object.name.endswith("l"):
        suffix = 'r'
    elif object.name.endswith("r"):
        suffix = 'l'
    else:  # what if the widget ends in .001?
        print('Object suffix unknown using blank')
        suffix = ''

    objectName = list(object.name)
    objectBaseName = objectName[:-1]
    mirroredObjectName = "".join(objectBaseName)+suffix

    if object.id_data.type == 'ARMATURE':
        return object.id_data.pose.bones.get(mirroredObjectName)
    else:
        return bpy.context.scene.objects.get(mirroredObjectName)


def findMatchBones():
    C = bpy.context
    D = bpy.data

    widgetsAndBones = {}

    if bpy.context.object.type == 'ARMATURE':
        for bone in C.selected_pose_bones:
            if bone.name.endswith("L") or bone.name.endswith("R"):
                widgetsAndBones[bone] = bone.custom_shape
                mirrorBone = findMirrorObject(bone)
                if mirrorBone:
                    widgetsAndBones[mirrorBone] = mirrorBone.custom_shape

        armature = bpy.context.object
        activeObject = C.active_pose_bone
    else:
        for shape in C.selected_objects:
            bone = fromWidgetFindBone(shape)
            if bone.name.endswith("L") or bone.name.endswith("R"):
                widgetsAndBones[fromWidgetFindBone(shape)] = shape

                mirrorShape = findMirrorObject(shape)
                if mirrorShape:
                    widgetsAndBones[mirrorShape] = mirrorShape

        activeObject = fromWidgetFindBone(C.object)
        armature = activeObject.id_data
    return (widgetsAndBones, activeObject, armature)
