import bpy
import numpy
from mathutils import Matrix
from .. import __package__


def getCollection(context):
    #check user preferences for the name of the collection
    if not context.preferences.addons[__package__].preferences.use_rigify_defaults:
        bw_collection_name = context.preferences.addons[__package__].preferences.bonewidget_collection_name
    else:
        bw_collection_name = "WGTS_" + context.active_object.name

    collection = recurLayerCollection(context.scene.collection, bw_collection_name)
    if collection:  # if it already exists
        return collection

    collection = bpy.data.collections.get(bw_collection_name)

    if collection:  # if it exists but not linked to scene
        context.scene.collection.children.link(collection)
        return collection

    else:  # create a new collection
        collection = bpy.data.collections.new(bw_collection_name)
        context.scene.collection.children.link(collection)
        # hide new collection
        viewlayer_collection = context.view_layer.layer_collection.children[collection.name]
        viewlayer_collection.hide_viewport = True
        return collection


def recurLayerCollection(layer_collection, collection_name):
    found = None
    if (layer_collection.name == collection_name):
        return layer_collection
    for layer in layer_collection.children:
        found = recurLayerCollection(layer, collection_name)
        if found:
            return found


def getViewLayerCollection(context, widget = None):
    widget_collection = bpy.data.collections[bpy.data.objects[widget.name].users_collection[0].name]
    #save current active layer_collection
    saved_layer_collection = bpy.context.view_layer.layer_collection
    # actually find the view_layer we want
    layer_collection = recurLayerCollection(saved_layer_collection, widget_collection.name)
    # make sure the collection (data level) is not hidden
    widget_collection.hide_viewport = False

    # change the active view layer
    bpy.context.view_layer.active_layer_collection = layer_collection
    # make sure it isn't excluded so it can be edited
    layer_collection.exclude = False
    #return the active view layer to what it was
    bpy.context.view_layer.active_layer_collection = saved_layer_collection

    return layer_collection


def boneMatrix(widget, matchBone):
    if widget == None:
        return
    widget.matrix_local = matchBone.bone.matrix_local
    widget.matrix_world = matchBone.id_data.matrix_world @ matchBone.bone.matrix_local
    if matchBone.custom_shape_transform:
        #if it has a tranform override, apply this to the widget loc and rot
        org_scale = widget.matrix_world.to_scale()
        org_scale_mat = Matrix.Scale(1, 4, org_scale)
        target_matrix = matchBone.custom_shape_transform.id_data.matrix_world @ matchBone.custom_shape_transform.bone.matrix_local
        loc = target_matrix.to_translation()
        loc_mat  = Matrix.Translation(loc)
        rot = target_matrix.to_euler().to_matrix()
        widget.matrix_world = loc_mat @ rot.to_4x4() @ org_scale_mat

    if matchBone.use_custom_shape_bone_size:
        ob_scale = bpy.context.scene.objects[matchBone.id_data.name].scale
        widget.scale = [matchBone.bone.length * ob_scale[0], matchBone.bone.length * ob_scale[1], matchBone.bone.length * ob_scale[2]]

    #if the user has added any custom transforms to the bone widget display - calculate this too
    loc = matchBone.custom_shape_translation
    rot = matchBone.custom_shape_rotation_euler
    scale =  matchBone.custom_shape_scale_xyz
    widget.matrix_world = widget.matrix_world @ Matrix.LocRotScale(loc , rot, scale)

    widget.data.update()


def fromWidgetFindBone(widget):
    matchBone = None
    for ob in bpy.context.scene.objects:
        if ob.type == "ARMATURE":
            for bone in ob.pose.bones:
                if bone.custom_shape == widget:
                    matchBone = bone
    return matchBone


def createWidget(bone, widget, relative, size, scale, slide, rotation, collection, use_face_data, wireframe_width):
    C = bpy.context
    D = bpy.data

    if not C.preferences.addons[__package__].preferences.use_rigify_defaults:
        bw_widget_prefix = C.preferences.addons[__package__].preferences.widget_prefix
    else:
        bw_widget_prefix = "WGT-" + C.active_object.name + "_"

    matrixBone = bone

    # delete the existing shape
    if bone.custom_shape:
        bpy.data.objects.remove(bpy.data.objects[bone.custom_shape.name], do_unlink=True)

    # make the data name include the prefix
    newData = D.meshes.new(bw_widget_prefix + bone.name)

    bone.use_custom_shape_bone_size = relative

    # deal with face data
    faces = widget['faces'] if use_face_data else []

    # add the verts
    newData.from_pydata(numpy.array(widget['vertices']) * [size[0] * scale[0], size[1] * scale[2],
                        size[2] * scale[1]], widget['edges'], faces)

    # Create tranform matrices (slide vector and rotation)
    widget_matrix = Matrix()
    trans = Matrix.Translation(slide)
    rot = rotation.to_matrix().to_4x4()

    # Translate then rotate the matrix
    widget_matrix = widget_matrix @ trans
    widget_matrix = widget_matrix @ rot

    # transform the widget with this matrix
    newData.transform(widget_matrix)

    newData.update(calc_edges=True)

    newObject = D.objects.new(bw_widget_prefix + bone.name, newData)

    newObject.data = newData
    newObject.name = bw_widget_prefix + bone.name
    collection.objects.link(newObject)

    newObject.matrix_world = bpy.context.active_object.matrix_world @ matrixBone.bone.matrix_local
    newObject.scale = [matrixBone.bone.length, matrixBone.bone.length, matrixBone.bone.length]
    layer = bpy.context.view_layer
    layer.update()

    bone.custom_shape = newObject
    bone.bone.show_wire = not use_face_data # show faces if use face data is enabled

    if bpy.app.version >= (4,2,0):
        bone.custom_shape_wire_width = wireframe_width


def symmetrizeWidget(bone, collection):
    C = bpy.context
    D = bpy.data

    if not C.preferences.addons[__package__].preferences.use_rigify_defaults:
        bw_widget_prefix = C.preferences.addons[__package__].preferences.widget_prefix
        rigify_object_name = ''
    else:
        bw_widget_prefix = "WGT-"
        rigify_object_name = C.active_object.name + "_"

    widget = bone.custom_shape

    if findMirrorObject(bone):
        mirrorBone = findMirrorObject(bone)

        mirrorWidget = mirrorBone.custom_shape

        if mirrorWidget is not None:
            if mirrorWidget != widget:
                if C.scene.objects.get(mirrorWidget.name):
                    D.objects.remove(mirrorWidget)

        newData = widget.data.copy()
        for vert in newData.vertices:
            vert.co = numpy.array(vert.co) * (-1, 1, 1)

        newObject = widget.copy()
        newObject.data = newData
        newData.update()
        newObject.name = bw_widget_prefix + rigify_object_name + findMirrorObject(bone).name
        D.collections[collection.name].objects.link(newObject)

        #if there is a override transform, use that bone matrix in the next step
        if findMirrorObject(bone).custom_shape_transform:
             mirrorBone = findMirrorObject(bone).custom_shape_transform

        newObject.matrix_local = mirrorBone.bone.matrix_local
        newObject.scale = [mirrorBone.bone.length, mirrorBone.bone.length, mirrorBone.bone.length]
        newObject.data.flip_normals()
        
        layer = bpy.context.view_layer
        layer.update()

        findMirrorObject(bone).custom_shape = newObject
        mirrorBone.bone.show_wire = bone.bone.show_wire

        if bpy.app.version >= (4,2,0):
            mirrorBone.custom_shape_wire_width = bone.custom_shape_wire_width

    else:
        pass


def symmetrizeWidget_helper(bone, collection, activeObject, widgetsAndBones):
    C = bpy.context

    bw_symmetry_suffix = C.preferences.addons[__package__].preferences.symmetry_suffix
    bw_symmetry_suffix = bw_symmetry_suffix.split(";")

    suffix_1 = bw_symmetry_suffix[0].replace(" ", "")
    suffix_2 = bw_symmetry_suffix[1].replace(" ", "")

    if activeObject.name.endswith(suffix_1):
        if bone.name.endswith(suffix_1) and widgetsAndBones[bone]:
            symmetrizeWidget(bone, collection)
    elif activeObject.name.endswith(suffix_2):
        if bone.name.endswith(suffix_2) and widgetsAndBones[bone]:
            symmetrizeWidget(bone, collection)


def deleteUnusedWidgets():
    C = bpy.context
    D = bpy.data

    if not C.preferences.addons[__package__].preferences.use_rigify_defaults:
        bw_collection_name = C.preferences.addons[__package__].preferences.bonewidget_collection_name
    else:
        bw_collection_name = 'WGTS_' + C.active_object.name

    collection = recurLayerCollection(C.scene.collection, bw_collection_name)
    widgetList = []

    for ob in D.objects:
        if ob.type == 'ARMATURE':
            for bone in ob.pose.bones:
                if bone.custom_shape:
                    widgetList.append(bone.custom_shape)

    unwantedList = [
        ob for ob in collection.all_objects if ob not in widgetList]
    # save the current context mode
    mode = C.mode
    # jump into object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    # delete unwanted widgets
    for ob in unwantedList:
        bpy.data.objects.remove(bpy.data.objects[ob.name], do_unlink=True)
    # jump back to current mode
    bpy.ops.object.mode_set(mode=mode)
    return


def editWidget(active_bone):
    C = bpy.context
    D = bpy.data
    widget = active_bone.custom_shape

    collection = getViewLayerCollection(C, widget)
    collection.hide_viewport = False

    # hide all other objects in collection
    for obj in collection.collection.all_objects:
        if obj.name != widget.name:
            obj.hide_set(True)
        else:
            obj.hide_set(False) # in case user manually hid it

    armature = active_bone.id_data
    bpy.ops.object.mode_set(mode='OBJECT')
    C.active_object.select_set(False)

    if C.space_data.local_view:
        bpy.ops.view3d.localview()

    # select object and make it active
    widget.select_set(True)
    bpy.context.view_layer.objects.active = widget
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.tool_settings.mesh_select_mode = (True, False, False) # enter vertex mode


def returnToArmature(widget):
    C = bpy.context
    D = bpy.data

    bone = fromWidgetFindBone(widget)
    armature = bone.id_data

    if C.active_object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')

    collection = getViewLayerCollection(C, widget)
    collection.hide_viewport = True

    # unhide all objects in the collection
    for obj in collection.collection.all_objects:
        obj.hide_set(False)
    
    if C.space_data.local_view:
        bpy.ops.view3d.localview()
    
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    armature.data.bones[bone.name].select = True
    armature.data.bones.active = armature.data.bones[bone.name]


def findMirrorObject(object):
    C = bpy.context
    D = bpy.data

    bw_symmetry_suffix = C.preferences.addons[__package__].preferences.symmetry_suffix
    bw_symmetry_suffix = bw_symmetry_suffix.split(";")

    suffix_1 = bw_symmetry_suffix[0].replace(" ", "")
    suffix_2 = bw_symmetry_suffix[1].replace(" ", "")

    if object.name.endswith(suffix_1):
        suffix = suffix_2
        suffix_length = len(suffix_1)

    elif object.name.endswith(suffix_2):
        suffix = suffix_1
        suffix_length = len(suffix_2)

    elif object.name.endswith(suffix_1.lower()):
        suffix = suffix_2.lower()
        suffix_length = len(suffix_1)
    elif object.name.endswith(suffix_2.lower()):
        suffix = suffix_1.lower()
        suffix_length = len(suffix_2)
    else:  # what if the widget ends in .001?
        print('Object suffix unknown, using blank')
        suffix = ''

    objectName = list(object.name)
    objectBaseName = objectName[:-suffix_length]
    mirroredObjectName = "".join(objectBaseName) + suffix

    if object.id_data.type == 'ARMATURE':
        return object.id_data.pose.bones.get(mirroredObjectName)
    else:
        return bpy.context.scene.objects.get(mirroredObjectName)


def findMatchBones():
    C = bpy.context
    D = bpy.data

    bw_symmetry_suffix = C.preferences.addons[__package__].preferences.symmetry_suffix
    bw_symmetry_suffix = bw_symmetry_suffix.split(";")

    suffix_1 = bw_symmetry_suffix[0].replace(" ", "")
    suffix_2 = bw_symmetry_suffix[1].replace(" ", "")

    widgetsAndBones = {}

    if bpy.context.object.type == 'ARMATURE':
        for bone in C.selected_pose_bones:
            if bone.name.endswith(suffix_1) or bone.name.endswith(suffix_2):
                widgetsAndBones[bone] = bone.custom_shape
                mirrorBone = findMirrorObject(bone)
                if mirrorBone:
                    widgetsAndBones[mirrorBone] = mirrorBone.custom_shape

        armature = bpy.context.object
        activeObject = C.active_pose_bone
    else:
        for shape in C.selected_objects:
            bone = fromWidgetFindBone(shape)
            if bone.name.endswith(("L","R")):
                widgetsAndBones[fromWidgetFindBone(shape)] = shape

                mirrorShape = findMirrorObject(shape)
                if mirrorShape:
                    widgetsAndBones[mirrorShape] = mirrorShape

        activeObject = fromWidgetFindBone(C.object)
        armature = activeObject.id_data
    return (widgetsAndBones, activeObject, armature)


def resyncWidgetNames():
    C = bpy.context
    D = bpy.data

    if not C.preferences.addons[__package__].preferences.use_rigify_defaults:
        bw_collection_name = C.preferences.addons[__package__].preferences.bonewidget_collection_name
        bw_widget_prefix = C.preferences.addons[__package__].preferences.widget_prefix
    else:
        bw_collection_name = 'WGTS_' + C.active_object.name
        bw_widget_prefix = 'WGT-' + C.active_object.name + '_'

    widgetsAndBones = {}

    if bpy.context.object.type == 'ARMATURE':
        for bone in C.active_object.pose.bones:
            if bone.custom_shape:
                widgetsAndBones[bone] = bone.custom_shape

    for k, v in widgetsAndBones.items():
        if k.name != (bw_widget_prefix + k.name):
            D.objects[v.name].name = str(bw_widget_prefix + k.name)


def clearBoneWidgets():
    C = bpy.context
    D = bpy.data

    if bpy.context.object.type == 'ARMATURE':
        for bone in C.selected_pose_bones:
            if bone.custom_shape:
                bone.custom_shape = None
                bone.custom_shape_transform = None


def addObjectAsWidget(context, collection):
    selected_objects = bpy.context.selected_objects

    if len(selected_objects) != 2:
        print('Only a widget object and the pose bone(s)')
        return{'FINISHED'}

    allowed_object_types = ['MESH','CURVE']

    widget_object = None

    for ob in selected_objects:
        if ob.type in allowed_object_types:
            widget_object = ob

    if widget_object:
        active_bone = context.active_pose_bone

        # deal with any existing shape
        if active_bone.custom_shape:
            bpy.data.objects.remove(bpy.data.objects[active_bone.custom_shape.name], do_unlink=True)

        #duplicate shape
        widget = widget_object.copy()
        widget.data = widget.data.copy()
        # reamame it
        bw_widget_prefix = context.preferences.addons[__package__].preferences.widget_prefix
        widget_name = bw_widget_prefix + active_bone.name
        widget.name = widget_name
        widget.data.name = widget_name
        # link it
        collection.objects.link(widget)

        # match transforms
        widget.matrix_world = bpy.context.active_object.matrix_world @ active_bone.bone.matrix_local
        widget.scale = [active_bone.bone.length, active_bone.bone.length, active_bone.bone.length]
        layer = bpy.context.view_layer
        layer.update()

        active_bone.custom_shape = widget
        active_bone.bone.show_wire = True

        #deselect original object
        widget_object.select_set(False)


def advanced_options_toggled(self, context):
    if self.advanced_options:
        self.global_size_advanced = (self.global_size_simple,) * 3
        self.slide_advanced[1] = self.slide_simple
    else:
        self.global_size_simple = self.global_size_advanced[1]
        self.slide_simple = self.slide_advanced[1]
