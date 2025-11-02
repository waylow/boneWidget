import bpy
import numpy
from mathutils import Matrix, Vector
from .. import __package__


def get_collection(context):
    # check user preferences for the name of the collection
    if not get_preferences(context).use_rigify_defaults:
        bw_collection_name = get_preferences(
            context).bonewidget_collection_name
    else:
        bw_collection_name = "WGTS_" + context.active_object.name

    collection = recursive_layer_collection(
        context.scene.collection, bw_collection_name)
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


def get_view_layer_collection(context, widget=None):
    widget_collection = bpy.data.collections[bpy.data.objects[widget.name].users_collection[0].name]
    # save current active layer_collection
    saved_layer_collection = bpy.context.view_layer.layer_collection
    # actually find the view_layer we want
    layer_collection = recursive_layer_collection(
        saved_layer_collection, widget_collection.name)
    # make sure the collection (data level) is not hidden
    widget_collection.hide_viewport = False

    # change the active view layer
    bpy.context.view_layer.active_layer_collection = layer_collection
    # make sure it isn't excluded so it can be edited
    layer_collection.exclude = False
    # return the active view layer to what it was
    bpy.context.view_layer.active_layer_collection = saved_layer_collection

    return layer_collection


def match_bone_matrix(widget, match_bone):
    if widget == None:
        return
    widget.matrix_local = match_bone.bone.matrix_local
    widget.matrix_world = match_bone.id_data.matrix_world @ match_bone.bone.matrix_local
    if match_bone.custom_shape_transform:
        # if it has a transform override, apply this to the widget loc and rot
        org_scale = widget.matrix_world.to_scale()
        org_scale_mat = Matrix.Scale(1, 4, org_scale)
        target_matrix = match_bone.custom_shape_transform.id_data.matrix_world @ match_bone.custom_shape_transform.bone.matrix_local
        loc = target_matrix.to_translation()
        loc_mat = Matrix.Translation(loc)
        rot = target_matrix.to_euler().to_matrix()
        widget.matrix_world = loc_mat @ rot.to_4x4() @ org_scale_mat

    if match_bone.use_custom_shape_bone_size:
        ob_scale = bpy.context.scene.objects[match_bone.id_data.name].scale
        widget.scale = [match_bone.bone.length * ob_scale[0],
                        match_bone.bone.length * ob_scale[1], match_bone.bone.length * ob_scale[2]]

    # if the user has added any custom transforms to the bone widget display - calculate this too
    loc = match_bone.custom_shape_translation
    rot = match_bone.custom_shape_rotation_euler
    scale = match_bone.custom_shape_scale_xyz
    widget.scale *= scale
    widget.matrix_world = widget.matrix_world @ Matrix.LocRotScale(
        loc, rot, widget.scale)

    widget.data.update()


def from_widget_find_bone(widget):
    match_bone = None
    for ob in bpy.context.scene.objects:
        if ob.type == "ARMATURE":
            for bone in ob.pose.bones:
                if bone.custom_shape == widget:
                    match_bone = bone
    return match_bone


def create_widget(bone, widget, relative, size, slide, rotation, collection, use_face_data, wireframe_width):
    if not get_preferences(bpy.context).use_rigify_defaults:
        bw_widget_prefix = get_preferences(bpy.context).widget_prefix
    else:
        bw_widget_prefix = "WGT-" + bpy.context.active_object.name + "_"

    matrix_bone = bone

    # delete the existing shape
    if bone.custom_shape:
        bpy.data.objects.remove(
            bpy.data.objects[bone.custom_shape.name], do_unlink=True)

    # make the data name include the prefix
    new_data = bpy.data.meshes.new(bw_widget_prefix + bone.name)

    bone.use_custom_shape_bone_size = relative

    # deal with face data
    faces = widget['faces'] if use_face_data else []

    # add the verts
    new_data.from_pydata(numpy.array(
        widget['vertices']) * size, widget['edges'], faces)

    # Create transform matrices (slide vector and rotation)
    widget_matrix = Matrix()

    # make the slide value always relative to the bone length
    if not relative:  # TODO: shift this to user preference?
        slide = Vector(slide)  # turn slide into a vector
        slide *= bone.length
    trans = Matrix.Translation(slide)

    rot = rotation.to_matrix().to_4x4()

    # Translate then rotate the matrix
    widget_matrix = widget_matrix @ trans
    widget_matrix = widget_matrix @ rot

    # transform the widget with this matrix
    new_data.transform(widget_matrix)

    new_data.update(calc_edges=True)

    new_object = bpy.data.objects.new(bw_widget_prefix + bone.name, new_data)

    new_object.data = new_data
    new_object.name = bw_widget_prefix + bone.name
    collection.objects.link(new_object)

    new_object.matrix_world = bpy.context.active_object.matrix_world @ matrix_bone.bone.matrix_local
    new_object.scale = [matrix_bone.bone.length,
                        matrix_bone.bone.length, matrix_bone.bone.length]
    layer = bpy.context.view_layer
    layer.update()

    bone.custom_shape = new_object
    # show faces if use face data is enabled
    bone.bone.show_wire = not use_face_data

    if bpy.app.version >= (4, 2, 0):
        bone.custom_shape_wire_width = wireframe_width


def symmetrize_widget(bone, collection):
    if not get_preferences(bpy.context).use_rigify_defaults:
        bw_widget_prefix = get_preferences(bpy.context).widget_prefix
        rigify_object_name = ''
    else:
        bw_widget_prefix = "WGT-"
        rigify_object_name = bpy.context.active_object.name + "_"

    mirror_bone = find_mirror_object(bone)
    if not mirror_bone:
        return

    widget = bone.custom_shape
    if not widget or not widget.data:
        return

    # clean up existing mirrored widget if it's different
    mirror_widget = mirror_bone.custom_shape
    if mirror_widget and mirror_widget != widget:
        existing = bpy.context.scene.objects.get(mirror_widget.name)
        if existing:
            bpy.data.objects.remove(existing)

    # create mirrored mesh data
    new_data = widget.data.copy()
    for vert in new_data.vertices:
        vert.co.x *= -1  # mirror along X-axis

    new_object = widget.copy()
    new_object.data = new_data
    new_object.name = bw_widget_prefix + rigify_object_name + mirror_bone.name
    bpy.data.collections[collection.name].objects.link(new_object)

    # use custom shape transform if available
    transform_bone = mirror_bone.custom_shape_transform or mirror_bone
    new_object.matrix_local = transform_bone.bone.matrix_local
    new_object.scale = [transform_bone.bone.length] * 3
    new_object.data.flip_normals()

    bpy.context.view_layer.update()

    mirror_bone.custom_shape = new_object
    mirror_bone.bone.show_wire = bone.bone.show_wire
    mirror_bone.use_custom_shape_bone_size = bone.use_custom_shape_bone_size

    symmetrize_color = get_preferences(bpy.context).symmetrize_color
    if bpy.app.version >= (4, 0, 0) and symmetrize_color:
        # pose bone colors
        mirror_bone.bone.color.custom.normal = bone.bone.color.custom.normal
        mirror_bone.bone.color.custom.select = bone.bone.color.custom.select
        mirror_bone.bone.color.custom.active = bone.bone.color.custom.active
        mirror_bone.bone.color.palette = bone.bone.color.palette

        # edit bone colors
        mirror_bone.color.custom.normal = bone.color.custom.normal
        mirror_bone.color.custom.select = bone.color.custom.select
        mirror_bone.color.custom.active = bone.color.custom.active
        mirror_bone.color.palette = bone.color.palette

    if bpy.app.version >= (4, 2, 0):
        mirror_bone.custom_shape_wire_width = bone.custom_shape_wire_width


def symmetrize_widget_helper(bone, collection, active_object, widgets_and_bones):
    bw_symmetry_suffix = get_preferences(bpy.context).symmetry_suffix
    bw_symmetry_suffix = bw_symmetry_suffix.split(";")

    suffix_1 = bw_symmetry_suffix[0].replace(" ", "")
    suffix_2 = bw_symmetry_suffix[1].replace(" ", "")

    if active_object.name.endswith(suffix_1):
        if bone.name.endswith(suffix_1) and widgets_and_bones[bone]:
            symmetrize_widget(bone, collection)
    elif active_object.name.endswith(suffix_2):
        if bone.name.endswith(suffix_2) and widgets_and_bones[bone]:
            symmetrize_widget(bone, collection)


def delete_unused_widgets():
    if not get_preferences(bpy.context).use_rigify_defaults:
        bw_collection_name = get_preferences(
            bpy.context).bonewidget_collection_name
    else:
        bw_collection_name = 'WGTS_' + bpy.context.active_object.name

    collection = recursive_layer_collection(
        bpy.context.scene.collection, bw_collection_name)
    widget_list = []

    for ob in bpy.data.objects:
        if ob.type == 'ARMATURE':
            for bone in ob.pose.bones:
                if bone.custom_shape:
                    widget_list.append(bone.custom_shape)

    unwanted_list = [
        ob for ob in collection.all_objects if ob not in widget_list]

    for ob in unwanted_list:
        bpy.data.objects.remove(bpy.data.objects[ob.name], do_unlink=True)

    return


def edit_widget(active_bone):
    widget = active_bone.custom_shape

    collection = get_view_layer_collection(bpy.context, widget)
    collection.hide_viewport = False

    # hide all other objects in collection
    for obj in collection.collection.all_objects:
        if obj.name != widget.name:
            obj.hide_set(True)
        else:
            obj.hide_set(False)  # in case user manually hid it

    armature = active_bone.id_data
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.active_object.select_set(False)

    if bpy.context.space_data.local_view:
        bpy.ops.view3d.localview()

    # select object and make it active
    widget.select_set(True)
    bpy.context.view_layer.objects.active = widget
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.tool_settings.mesh_select_mode = (
        True, False, False)  # enter vertex mode


def return_to_armature(widget):
    bone = from_widget_find_bone(widget)
    armature = bone.id_data

    if bpy.context.active_object.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='DESELECT')

    collection = get_view_layer_collection(bpy.context, widget)
    collection.hide_viewport = True

    # unhide all objects in the collection
    for obj in collection.collection.all_objects:
        obj.hide_set(False)

    if bpy.context.space_data.local_view:
        bpy.ops.view3d.localview()

    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    if bpy.app.version < (5, 0, 0):
        armature.data.bones[bone.name].select = True
    armature.data.bones.active = armature.data.bones[bone.name]


def find_mirror_object(object):
    bw_symmetry_suffix = get_preferences(bpy.context).symmetry_suffix
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

    object_name = list(object.name)
    object_base_name = object_name[:-suffix_length]
    mirrored_object_name = "".join(object_base_name) + suffix

    if object.id_data.type == 'ARMATURE':
        return object.id_data.pose.bones.get(mirrored_object_name)
    else:
        return bpy.context.scene.objects.get(mirrored_object_name)


def find_match_bones():
    bw_symmetry_suffix = get_preferences(bpy.context).symmetry_suffix
    bw_symmetry_suffix = bw_symmetry_suffix.split(";")

    suffix_1 = bw_symmetry_suffix[0].replace(" ", "")
    suffix_2 = bw_symmetry_suffix[1].replace(" ", "")

    widgets_and_bones = {}

    if bpy.context.object.type == 'ARMATURE':
        for bone in bpy.context.selected_pose_bones:
            if bone.name.endswith(suffix_1) or bone.name.endswith(suffix_2):
                widgets_and_bones[bone] = bone.custom_shape
                mirror_bone = find_mirror_object(bone)
                if mirror_bone:
                    widgets_and_bones[mirror_bone] = mirror_bone.custom_shape

        armature = bpy.context.object
        active_object = bpy.context.active_pose_bone
    else:
        for shape in bpy.context.selected_objects:
            bone = from_widget_find_bone(shape)
            if bone.name.endswith(("L", "R")):
                widgets_and_bones[from_widget_find_bone(shape)] = shape

                mirrorShape = find_mirror_object(shape)
                if mirrorShape:
                    widgets_and_bones[mirrorShape] = mirrorShape

        active_object = from_widget_find_bone(bpy.context.object)
        armature = active_object.id_data
    return (widgets_and_bones, active_object, armature)


def resync_widget_names():
    if not get_preferences(bpy.context).use_rigify_defaults:
        bw_collection_name = get_preferences(
            bpy.context).bonewidget_collection_name
        bw_widget_prefix = get_preferences(bpy.context).widget_prefix
    else:
        bw_collection_name = 'WGTS_' + bpy.context.active_object.name
        bw_widget_prefix = 'WGT-' + bpy.context.active_object.name + '_'

    widgets_and_bones = {}

    if bpy.context.object.type == 'ARMATURE':
        for bone in bpy.context.active_object.pose.bones:
            if bone.custom_shape:
                widgets_and_bones[bone] = bone.custom_shape

    for k, v in widgets_and_bones.items():
        if k.name != (bw_widget_prefix + k.name):
            bpy.data.objects[v.name].name = str(bw_widget_prefix + k.name)


def clear_bone_widgets():
    if bpy.context.object.type == 'ARMATURE':
        for bone in bpy.context.selected_pose_bones:
            if bone.custom_shape:
                bone.custom_shape = None
                bone.custom_shape_transform = None


def add_object_as_widget(context, collection):
    selected_objects = bpy.context.selected_objects

    if len(selected_objects) != 2:
        print('Only a widget object and the pose bone(s)')
        return {'FINISHED'}

    allowed_object_types = ['MESH', 'CURVE']

    widget_object = None

    for ob in selected_objects:
        if ob.type in allowed_object_types:
            widget_object = ob

    if widget_object:
        active_bone = context.active_pose_bone

        # deal with any existing shape
        if active_bone.custom_shape:
            bpy.data.objects.remove(
                bpy.data.objects[active_bone.custom_shape.name], do_unlink=True)

        # duplicate shape
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
        widget.scale = [active_bone.bone.length,
                        active_bone.bone.length, active_bone.bone.length]
        layer = bpy.context.view_layer
        layer.update()

        active_bone.custom_shape = widget
        active_bone.bone.show_wire = True

        # deselect original object
        widget_object.select_set(False)


def set_bone_color(context, color, clear_both_modes=None):
    if context.object.mode == "POSE":
        if color == 'DEFAULT' and clear_both_modes != None:
            for bone in context.selected_pose_bones:
                bone.color.palette = 'DEFAULT'

                if clear_both_modes:
                    bone.bone.color.palette = 'DEFAULT'
            return

        for bone in context.selected_pose_bones:
            bone.color.palette = color  # this will get the selected bone color

            if color == "CUSTOM":
                bone.color.custom.normal = context.scene.custom_pose_color_set.normal
                bone.color.custom.select = context.scene.custom_pose_color_set.select
                bone.color.custom.active = context.scene.custom_pose_color_set.active

            # set the edit bone colors if applicable (while in pose mode)
            if get_preferences(context).edit_bone_colors == 'DEFAULT':
                bone.bone.color.palette = 'DEFAULT'  # this will reset the edit bone color

            elif get_preferences(context).edit_bone_colors == 'LINKED':
                bone.bone.color.palette = color  # set the edit bone colors

                # Set the custom color to edit bones (if applicable)
                if color == "CUSTOM":
                    bone.bone.color.custom.normal = context.scene.custom_pose_color_set.normal
                    bone.bone.color.custom.select = context.scene.custom_pose_color_set.select
                    bone.bone.color.custom.active = context.scene.custom_pose_color_set.active

    elif context.object.mode == "EDIT":
        if color == 'DEFAULT' and clear_both_modes != None:
            for edit_bone in context.selected_bones:
                edit_bone.color.palette = 'DEFAULT'

                if clear_both_modes:
                    pose_bone = context.object.pose.bones.get(edit_bone.name)
                    pose_bone.color.palette = 'DEFAULT'

            return

        for edit_bone in context.selected_bones:
            if get_preferences(context).edit_bone_colors == 'DEFAULT':
                # this will get the edit bone color back to default
                edit_bone.color.palette = 'DEFAULT'

            elif get_preferences(context).edit_bone_colors == 'LINKED':
                edit_bone.color.palette = color  # set the edit mode color

                # get the pose bone
                pose_bone = context.object.pose.bones.get(edit_bone.name)
                pose_bone.color.palette = color  # set the pose mode color

                if color == "CUSTOM":
                    # set edit bone custom colors
                    edit_bone.color.custom.normal = context.scene.custom_edit_color_set.normal
                    edit_bone.color.custom.select = context.scene.custom_edit_color_set.select
                    edit_bone.color.custom.active = context.scene.custom_edit_color_set.active
                    # set pose bone custom colors
                    pose_bone.color.custom.normal = context.scene.custom_edit_color_set.normal
                    pose_bone.color.custom.select = context.scene.custom_edit_color_set.select
                    pose_bone.color.custom.active = context.scene.custom_edit_color_set.active

            elif get_preferences(context).edit_bone_colors == 'SEPARATE':
                edit_bone.color.palette = color  # set the edit mode color

                if color == "CUSTOM":
                    # set edit bone custom colors
                    edit_bone.color.custom.normal = context.scene.custom_edit_color_set.normal
                    edit_bone.color.custom.select = context.scene.custom_edit_color_set.select
                    edit_bone.color.custom.active = context.scene.custom_edit_color_set.active


def copy_bone_color(context, bone):
    live_update_current_state = context.scene.live_update_on
    context.scene.live_update_on = False

    if bone.color.is_custom:
        if context.object.mode == 'POSE':
            context.scene.custom_pose_color_set.normal = bone.color.custom.normal
            context.scene.custom_pose_color_set.select = bone.color.custom.select
            context.scene.custom_pose_color_set.active = bone.color.custom.active
        else:
            context.scene.custom_edit_color_set.normal = bone.color.custom.normal
            context.scene.custom_edit_color_set.select = bone.color.custom.select
            context.scene.custom_edit_color_set.active = bone.color.custom.active
    elif bone.color.palette != "DEFAULT":  # bone has a theme assigned
        theme = bone.color.palette
        theme_id = int(theme[-2:]) - 1
        theme_color_set = bpy.context.preferences.themes[0].bone_color_sets[theme_id]

        palette = context.scene.custom_pose_color_set if context.object.mode == 'POSE' \
            else context.scene.custom_edit_color_set

        palette.normal = theme_color_set.normal
        palette.select = theme_color_set.select
        palette.active = theme_color_set.active

    context.scene.live_update_on = live_update_current_state


def update_bone_color(self, context):
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
        items.append((f"THEME{i:02}", f"Theme {i:02}",
                     "", f"COLORSET_{i:02}_VEC", i))
    return items


def bone_color_items_short(self, context):
    items = []
    for i in range(1, 16):
        items.append((f"THEME{i:02}", f"Theme {i:02}",
                     "", f"COLORSET_{i:02}_VEC", i))
    items.append(("CUSTOM", "Custom", "", "COLOR", 16))
    return items


def live_update_toggle(self, context):
    context.scene.live_update_on = self.live_update_toggle


def get_preferences(context):
    return context.preferences.addons[__package__].preferences
