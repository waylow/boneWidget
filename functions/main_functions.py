import bpy
import numpy
from mathutils import Matrix
from .. import __package__


def get_collection(context):
    #check user preferences for the name of the collection
    if not get_preferences(context).use_rigify_defaults:
        bw_collection_name = get_preferences(context).bonewidget_collection_name
    else:
        bw_collection_name = "WGTS_" + context.active_object.name

    collection = recursive_layer_collection(context.scene.collection, bw_collection_name)
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


def recursive_layer_collection(layer_collection, collection_name):
    found = None
    if (layer_collection.name == collection_name):
        return layer_collection
    for layer in layer_collection.children:
        found = recursive_layer_collection(layer, collection_name)
        if found:
            return found


def get_view_layer_collection(context, widget = None):
    widget_collection = bpy.data.collections[bpy.data.objects[widget.name].users_collection[0].name]
    #save current active layer_collection
    saved_layer_collection = bpy.context.view_layer.layer_collection
    # actually find the view_layer we want
    layer_collection = recursive_layer_collection(saved_layer_collection, widget_collection.name)
    # make sure the collection (data level) is not hidden
    widget_collection.hide_viewport = False

    # change the active view layer
    bpy.context.view_layer.active_layer_collection = layer_collection
    # make sure it isn't excluded so it can be edited
    layer_collection.exclude = False
    #return the active view layer to what it was
    bpy.context.view_layer.active_layer_collection = saved_layer_collection

    return layer_collection


def match_bone_matrix(widget, matchBone):
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

    # if the user has added any custom transforms to the bone widget display - calculate this too
    loc = matchBone.custom_shape_translation
    rot = matchBone.custom_shape_rotation_euler
    scale =  matchBone.custom_shape_scale_xyz
    widget.scale *= scale
    widget.matrix_world = widget.matrix_world @ Matrix.LocRotScale(loc , rot, widget.scale)

    widget.data.update()


def from_widget_find_bone(widget):
    matchBone = None
    for ob in bpy.context.scene.objects:
        if ob.type == "ARMATURE":
            for bone in ob.pose.bones:
                if bone.custom_shape == widget:
                    matchBone = bone
    return matchBone


def create_widget(bone, widget, relative, size, slide, rotation, collection, use_face_data, wireframe_width, bone_color):
    C = bpy.context
    D = bpy.data

    if not get_preferences(C).use_rigify_defaults:
        bw_widget_prefix = get_preferences(C).widget_prefix
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
    newData.from_pydata(numpy.array(widget['vertices']) * size, widget['edges'], faces)

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

    if bpy.app.version >= (4,0,0):    
        bone.bone.color.palette = bone_color #this will copy the selected pose bone color
    
    if bpy.app.version >= (4,2,0):
        bone.custom_shape_wire_width = wireframe_width
        bone.bone.color.palette = bone_color


def symmetrize_widget(bone, collection):
    C = bpy.context
    D = bpy.data

    if not get_preferences(C).use_rigify_defaults:
        bw_widget_prefix = get_preferences(C).widget_prefix
        rigify_object_name = ''
    else:
        bw_widget_prefix = "WGT-"
        rigify_object_name = C.active_object.name + "_"

    widget = bone.custom_shape

    if find_mirror_object(bone):
        mirrorBone = find_mirror_object(bone)

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
        newObject.name = bw_widget_prefix + rigify_object_name + find_mirror_object(bone).name
        D.collections[collection.name].objects.link(newObject)

        #if there is a override transform, use that bone matrix in the next step
        if find_mirror_object(bone).custom_shape_transform:
             mirrorBone = find_mirror_object(bone).custom_shape_transform

        newObject.matrix_local = mirrorBone.bone.matrix_local
        newObject.scale = [mirrorBone.bone.length, mirrorBone.bone.length, mirrorBone.bone.length]
        newObject.data.flip_normals()
        
        layer = bpy.context.view_layer
        layer.update()

        find_mirror_object(bone).custom_shape = newObject
        mirrorBone.bone.show_wire = bone.bone.show_wire

        if bpy.app.version >= (4,0,0):
            mirrorBone.bone.color.palette = bone.bone.color.palette # pose bone color
            mirrorBone.color.palette = bone.color.palette # edit bone color

        if bpy.app.version >= (4,2,0):
            mirrorBone.custom_shape_wire_width = bone.custom_shape_wire_width

    else:
        pass


def symmetrize_widget_helper(bone, collection, activeObject, widgetsAndBones):
    C = bpy.context

    bw_symmetry_suffix = get_preferences(C).symmetry_suffix
    bw_symmetry_suffix = bw_symmetry_suffix.split(";")

    suffix_1 = bw_symmetry_suffix[0].replace(" ", "")
    suffix_2 = bw_symmetry_suffix[1].replace(" ", "")

    if activeObject.name.endswith(suffix_1):
        if bone.name.endswith(suffix_1) and widgetsAndBones[bone]:
            symmetrize_widget(bone, collection)
    elif activeObject.name.endswith(suffix_2):
        if bone.name.endswith(suffix_2) and widgetsAndBones[bone]:
            symmetrize_widget(bone, collection)


def delete_unused_widgets():
    C = bpy.context
    D = bpy.data

    if not get_preferences(C).use_rigify_defaults:
        bw_collection_name = get_preferences(C).bonewidget_collection_name
    else:
        bw_collection_name = 'WGTS_' + C.active_object.name

    collection = recursive_layer_collection(C.scene.collection, bw_collection_name)
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


def edit_widget(active_bone):
    C = bpy.context
    D = bpy.data
    widget = active_bone.custom_shape

    collection = get_view_layer_collection(C, widget)
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


def return_to_armature(widget):
    C = bpy.context
    D = bpy.data

    bone = from_widget_find_bone(widget)
    armature = bone.id_data

    if C.active_object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')

    collection = get_view_layer_collection(C, widget)
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


def find_mirror_object(object):
    C = bpy.context
    D = bpy.data

    bw_symmetry_suffix = get_preferences(C).symmetry_suffix
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


def find_match_bones():
    C = bpy.context
    D = bpy.data

    bw_symmetry_suffix = get_preferences(C).symmetry_suffix
    bw_symmetry_suffix = bw_symmetry_suffix.split(";")

    suffix_1 = bw_symmetry_suffix[0].replace(" ", "")
    suffix_2 = bw_symmetry_suffix[1].replace(" ", "")

    widgetsAndBones = {}

    if bpy.context.object.type == 'ARMATURE':
        for bone in C.selected_pose_bones:
            if bone.name.endswith(suffix_1) or bone.name.endswith(suffix_2):
                widgetsAndBones[bone] = bone.custom_shape
                mirrorBone = find_mirror_object(bone)
                if mirrorBone:
                    widgetsAndBones[mirrorBone] = mirrorBone.custom_shape

        armature = bpy.context.object
        activeObject = C.active_pose_bone
    else:
        for shape in C.selected_objects:
            bone = from_widget_find_bone(shape)
            if bone.name.endswith(("L","R")):
                widgetsAndBones[from_widget_find_bone(shape)] = shape

                mirrorShape = find_mirror_object(shape)
                if mirrorShape:
                    widgetsAndBones[mirrorShape] = mirrorShape

        activeObject = from_widget_find_bone(C.object)
        armature = activeObject.id_data
    return (widgetsAndBones, activeObject, armature)


def resync_widget_names():
    C = bpy.context
    D = bpy.data

    if not get_preferences(C).use_rigify_defaults:
        bw_collection_name = get_preferences(C).bonewidget_collection_name
        bw_widget_prefix = get_preferences(C).widget_prefix
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


def clear_bone_widgets():
    C = bpy.context
    D = bpy.data

    if bpy.context.object.type == 'ARMATURE':
        for bone in C.selected_pose_bones:
            if bone.custom_shape:
                bone.custom_shape = None
                bone.custom_shape_transform = None


def add_object_as_widget(context, collection):
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
        bw_widget_prefix = get_preferences(context).widget_prefix
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


def set_bone_color(context, color):
    '''This will reset the edit bone color to 'DEFAULT' but this will become a user preference later #TODO '''
    if context.object.mode == "POSE":
        for bone in context.selected_pose_bones:
            bone.color.palette = color #this will get the selected bone color
            bone.bone.color.palette = 'DEFAULT' # this will reset the edit bone color (override what rigify does)

            if color == "CUSTOM":
                bone.color.custom.normal = context.scene.custom_pose_color_set.normal
                bone.color.custom.select = context.scene.custom_pose_color_set.select
                bone.color.custom.active = context.scene.custom_pose_color_set.active
    elif context.object.mode == "EDIT":
        for bone in context.selected_bones:
            bone.color.palette = 'DEFAULT' #this will get the edit bone color back to default
            context.active_object.pose.bones[bone.name].color.palette = color
            
            if color == "CUSTOM":
                bone.color.custom.normal = context.scene.custom_edit_color_set.normal
                bone.color.custom.select = context.scene.custom_edit_color_set.select
                bone.color.custom.active = context.scene.custom_edit_color_set.active
    

def copy_bone_color(context, bone):
    live_update_current_state = context.scene.live_update_on
    context.scene.live_update_on = False
    
    if bone.color.is_custom:
        context.scene.custom_pose_color_set.normal = bone.color.custom.normal
        context.scene.custom_pose_color_set.select = bone.color.custom.select
        context.scene.custom_pose_color_set.active = bone.color.custom.active
    elif bone.color.palette != "DEFAULT": # bone has a theme assigned
        theme = bone.color.palette
        theme_id = int(theme[-2:]) - 1
        theme_color_set = bpy.context.preferences.themes[0].bone_color_sets[theme_id]

        context.scene.custom_pose_color_set.normal = theme_color_set.normal
        context.scene.custom_pose_color_set.select = theme_color_set.select
        context.scene.custom_pose_color_set.active = theme_color_set.active
        
    context.scene.live_update_on = live_update_current_state


def copy_edit_bone_color(context, bone):
    live_update_current_state = context.scene.live_update_on
    context.scene.live_update_on = False
    
    if bone.color.is_custom:
        context.scene.custom_edit_color_set.normal = bone.color.custom.normal
        context.scene.custom_edit_color_set.select = bone.color.custom.select
        context.scene.custom_edit_color_set.active = bone.color.custom.active
    elif bone.color.palette != "DEFAULT": # bone has a theme assigned
        theme = bone.color.palette
        theme_id = int(theme[-2:]) - 1
        theme_color_set = bpy.context.preferences.themes[0].bone_color_sets[theme_id]

        context.scene.custom_edit_color_set.normal = theme_color_set.normal
        context.scene.custom_edit_color_set.select = theme_color_set.select
        context.scene.custom_edit_color_set.active = theme_color_set.active
        
    context.scene.live_update_on = live_update_current_state


def uodate_bone_color(self, context):
    if context.scene.live_update_on:
        set_bone_color(context, "CUSTOM")


def advanced_options_toggled(self, context):
    if self.advanced_options:
        self.global_size_advanced = (self.global_size_simple,) * 3
        self.slide_advanced[1] = self.slide_simple
    else:
        self.global_size_simple = self.global_size_advanced[1]
        self.slide_simple = self.slide_advanced[1]


def bone_color_items(self, context):
    items = [("DEFAULT", "Default Colors", "", "", 0)]
    for i in range(1, 16):
        items.append((f"THEME{i:02}", f"Theme {i:02}", "", f"COLORSET_{i:02}_VEC", i))
    return items


def bone_color_items_short(self, context):
    items = []
    for i in range(1, 16):
        items.append((f"THEME{i:02}", f"Theme {i:02}", "", f"COLORSET_{i:02}_VEC", i))
    items.append(("CUSTOM", "Custom", "", "COLOR", 16))
    return items


def live_update_toggle(self, context):
    context.scene.live_update_on = self.live_update_toggle


def get_preferences(context):
    return context.preferences.addons[__package__].preferences
