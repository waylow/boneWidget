import bpy
import os

from .functions import (
    find_match_bones,
    from_widget_find_bone,
    symmetrize_widget_helper,
    match_bone_matrix,
    create_widget,
    edit_widget,
    return_to_armature,
    add_remove_widgets,
    get_widget_data,
    get_collection,
    get_view_layer_collection,
    recursive_layer_collection,
    delete_unused_widgets,
    clear_bone_widgets,
    resync_widget_names,
    add_object_as_widget,
    import_widget_library,
    export_widget_library,
    advanced_options_toggled,
    remove_custom_image,
    copy_custom_image,
    get_widget_data,
    update_custom_image,
    reset_default_images,
    update_widget_library,
    set_bone_color,
    copy_bone_color,
    bone_color_items,
    get_preferences,
    save_color_sets,
    load_color_presets,
    add_color_set,
    scan_armature_color_presets,
    import_color_presets,
    export_color_presets,
    update_color_presets,
    create_wireframe_copy,
    setup_viewport,
    restore_viewport_position,
    render_widget_thumbnail,
    add_camera_from_view,
    frame_object_with_padding
)

from .props import ImportColorSet, ImportItemData, get_import_options
from .classes import ColorSet

from bpy.props import FloatProperty, BoolProperty, FloatVectorProperty, IntVectorProperty, StringProperty, EnumProperty


class BONEWIDGET_OT_shared_property_group(bpy.types.PropertyGroup):
    """Storage class for Shared Attribute Properties"""

    custom_image_data = ("", "")
    import_library_filepath = ""
    color_sets: bpy.props.CollectionProperty(type=ImportColorSet)
    import_item_data: bpy.props.CollectionProperty(type=ImportItemData)
    image_collection = bpy.utils.previews.new()


class BONEWIDGET_OT_create_widget(bpy.types.Operator):
    """Creates a widget for selected bone"""
    bl_idname = "bonewidget.create_widget"
    bl_label = "Create Widget"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.mode == 'POSE')

    relative_size: BoolProperty(
        name="Scale to Bone length",
        default=True,
        description="Scale Widget to bone length"
    )

    use_face_data: BoolProperty(
        name="Use Face Data",
        default=False,
        description="When enabled this option will include the widget's face data (if available)"
    )

    advanced_options: BoolProperty(
        name="Advanced options",
        default=False,
        description="Show advanced options",
        update=advanced_options_toggled
    )

    global_size_simple: FloatProperty(
        name="Global Size",
        default=1.0,
        description="Global Size"
    )

    global_size_advanced: FloatVectorProperty(
        name="Global Size",
        default=(1.0, 1.0, 1.0),
        subtype='XYZ',
        description="Global Size"
    )

    slide_simple: FloatProperty(
        name="Slide",
        default=0.0,
        subtype='NONE',
        unit='NONE',
        description="Slide widget along bone y axis"
    )

    slide_advanced: FloatVectorProperty(
        name="Slide",
        default=(0.0, 0.0, 0.0),
        subtype='XYZ',
        unit='NONE',
        description="Slide widget along bone xyz axes"
    )

    rotation: FloatVectorProperty(
        name="Rotation",
        description="Rotate the widget",
        default=(0.0, 0.0, 0.0),
        subtype='EULER',
        unit='ROTATION',
        precision=1,
    )

    wireframe_width: FloatProperty(
        name="Wire Width",
        default=2.0,
        min=1.0,
        max=16,
        soft_max=10,
        description="Set the thickness of a wireframe widget"
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        row = col.row(align=True)
        row.prop(self, "relative_size")
        row = col.row(align=True)
        if self.advanced_options:
            row.prop(self, "use_face_data")
        row = col.row(align=True)
        row.prop(
            self, "global_size_advanced" if self.advanced_options else "global_size_simple", expand=False)
        row = col.row(align=True)
        row.prop(
            self, "slide_advanced" if self.advanced_options else "slide_simple", text="Slide")
        row = col.row(align=True)
        row.prop(self, "rotation", text="Rotation")
        row = col.row(align=True)
        if bpy.app.version >= (4, 2, 0):
            row.prop(self, "wireframe_width", text="Wire Width")
            row = col.row(align=True)
        row.prop(self, "advanced_options")

    def execute(self, context):
        widget_data = get_widget_data(context.window_manager.widget_list)
        slide = self.slide_advanced if self.advanced_options else (
            0.0, self.slide_simple, 0.0)
        global_size = self.global_size_advanced if self.advanced_options else (
            self.global_size_simple,) * 3
        use_face_data = self.use_face_data if self.advanced_options else False
        for bone in bpy.context.selected_pose_bones:
            create_widget(bone, widget_data, self.relative_size, global_size, slide, self.rotation,
                          get_collection(context), use_face_data, self.wireframe_width)
        return {'FINISHED'}


class BONEWIDGET_OT_edit_widget(bpy.types.Operator):
    """Edit the widget for selected bone"""
    bl_idname = "bonewidget.edit_widget"
    bl_label = "Edit Widget"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode == 'POSE'
                and context.active_pose_bone is not None and context.active_pose_bone.custom_shape is not None)

    def execute(self, context):
        active_bone = context.active_pose_bone
        try:
            edit_widget(active_bone)
        except KeyError:
            self.report({'INFO'}, 'This widget is the Widget Collection')
        return {'FINISHED'}


class BONEWIDGET_OT_return_to_armature(bpy.types.Operator):
    """Switch back to the armature"""
    bl_idname = "bonewidget.return_to_armature"
    bl_label = "Return to armature"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'MESH'
                and context.object.mode in ['EDIT', 'OBJECT'])

    def execute(self, context):
        b = bpy.context.object
        if from_widget_find_bone(bpy.context.object):
            return_to_armature(bpy.context.object)
        else:
            self.report({'INFO'}, 'Object is not a bone widget')
        return {'FINISHED'}


class BONEWIDGET_OT_match_bone_transforms(bpy.types.Operator):
    """Match the widget to the bone transforms"""
    bl_idname = "bonewidget.match_bone_transforms"
    bl_label = "Match bone transforms"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.mode == "POSE":
            for bone in bpy.context.selected_pose_bones:
                match_bone_matrix(bone.custom_shape, bone)

        else:
            for ob in bpy.context.selected_objects:
                if ob.type == 'MESH':
                    match_bone = from_widget_find_bone(ob)
                    if match_bone:
                        match_bone_matrix(ob, match_bone)
        return {'FINISHED'}


class BONEWIDGET_OT_match_symmetrize_shape(bpy.types.Operator):
    """Symmetrize to the opposite side ONLY if it is named with a .L or .R (default settings)"""
    bl_idname = "bonewidget.symmetrize_shape"
    bl_label = "Symmetrize"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE'
                and context.object.mode in ['POSE'])

    def execute(self, context):
        widget = bpy.context.active_pose_bone.custom_shape
        if widget is None:
            self.report({"INFO"}, "There is no widget on this bone.")
            return {'FINISHED'}
        collection = get_view_layer_collection(context, widget)
        widgets_and_bones = find_match_bones()[0]
        active_object = find_match_bones()[1]
        widgets_and_bones = find_match_bones()[0]

        if not active_object:
            self.report({"INFO"}, "No active bone or object")
            return {'FINISHED'}

        for bone in widgets_and_bones:
            symmetrize_widget_helper(
                bone, collection, active_object, widgets_and_bones)

        return {'FINISHED'}


class BONEWIDGET_OT_image_select(bpy.types.Operator):
    """Open a Fileselect browser and get the image location"""
    bl_idname = "bonewidget.image_select"
    bl_label = "Select Image"
    bl_options = {'INTERNAL'}

    filter_glob: StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;',
        options={'HIDDEN'}
    )

    filename: StringProperty(
        name='Filename',
        subtype='FILE_NAME',
        description='Name of custom image',
    )

    filepath: StringProperty(
        subtype="FILE_PATH"
    )

    def invoke(self, context, event):
        self.filename = ""
        context.window_manager.fileselect_add(self)
        if context.area:
            context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def execute(self, context):
        bpy.context.window_manager.prop_grp.custom_image_name = self.filename
        setattr(BONEWIDGET_OT_shared_property_group,
                "custom_image_data", (self.filepath, self.filename))
        context.area.tag_redraw()
        return {'FINISHED'}


class BONEWIDGET_OT_add_custom_image(bpy.types.Operator):
    """Add a custom image to selected preview panel widget"""
    bl_idname = "bonewidget.add_custom_image"
    bl_label = "Select Image"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;',
        options={'HIDDEN'}
    )

    filename: StringProperty(
        name='Filename',
        subtype='FILE_NAME',
        description='Name of custom image',
    )

    filepath: StringProperty(
        subtype="FILE_PATH"
    )

    def invoke(self, context, event):
        self.filename = ""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if self.filepath:
            # first remove previous custom image if present
            current_widget = context.window_manager.widget_list
            remove_custom_image(get_widget_data(current_widget).get("image"))
            # copy over the image to custom folder
            copy_custom_image(self.filepath, self.filename)
            # update the json files with new image data
            update_custom_image(self.filename)

            self.report({'INFO'}, "Custom image has been added!")
        return {'FINISHED'}


class BONEWIDGET_OT_add_widgets(bpy.types.Operator):
    """Add selected mesh object to Bone Widget Library and optionally Render Thumbnail"""
    bl_idname = "bonewidget.add_widgets"
    bl_label = "Add New Widget to Library"
    bl_options = {'UNDO'}

    widget_name: StringProperty(
        name="Widget Name",
        default="",
        description="The name of the new widget",
        options={"TEXTEDIT_UPDATE"},
    )

    image_mode: EnumProperty(
        name="Thumbnail",
        description="Choose how the widget image is handled",
        items=[
            ('AUTO_RENDER', "Auto Render", "Render the widget automatically"),
            ('CUSTOM_IMAGE', "Custom Image", "Use a custom image"),
            ('PLACEHOLDER_IMAGE', "Placeholder Image", "Use the placeholder image"),
        ],
        default='AUTO_RENDER'
    )

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'MESH' and context.object.mode == 'OBJECT'
                and context.active_object is not None)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Widget Name:")
        row.prop(self, "widget_name", text="")
        row = layout.row()

        # adding custom image this way doesn't work in blender 3.6
        if bpy.app.version > (3, 7, 0):
            row.prop(self, "image_mode")

            if self.image_mode == 'CUSTOM_IMAGE':
                row = layout.row()
                if bpy.app.version >= (4, 1, 0):
                    row.prop(bpy.context.window_manager.prop_grp, "custom_image_name",
                             text="", placeholder="Choose an image...", icon="FILE_IMAGE")
                else:
                    row.prop(bpy.context.window_manager.prop_grp,
                             "custom_image_name", text="", icon="FILE_IMAGE")
                row.operator('bonewidget.image_select',
                             icon='FILEBROWSER', text="")

    def invoke(self, context, event):
        if bpy.context.selected_objects:
            self.widget_name = context.active_object.name
            setattr(BONEWIDGET_OT_shared_property_group,
                    "custom_image_name", StringProperty(name="Image Name"))
            return context.window_manager.invoke_props_dialog(self)

        self.report({'WARNING'}, 'Please select an object first!')
        return {'CANCELLED'}

    def execute(self, context):
        objects = []
        if bpy.context.mode == "POSE":
            for bone in bpy.context.selected_pose_bones:
                objects.append(bone.custom_shape)
        else:
            for ob in bpy.context.selected_objects:
                if ob.type == 'MESH':
                    objects.append(ob)

        if not objects:
            self.report({'WARNING'}, 'Select Meshes or Pose bones')
            return {'CANCELLED'}

        # make sure widget name isn't empty
        if not self.widget_name:
            self.report({'WARNING'}, "Widget name can't be empty!")
            return {'CANCELLED'}

        # get filepath to custom image if specified and transfer to custom image folder
        custom_image_name = ""
        custom_image_path = ""
        message_extra = ""

        if self.image_mode == 'CUSTOM_IMAGE':
            # context.window_manager.custom_image
            custom_image_path, custom_image_name = bpy.context.window_manager.prop_grp.custom_image_data

            # no image path found
            if not custom_image_path:
                # check if user pasted an image path into text field
                text_field = bpy.context.window_manager.prop_grp.custom_image_name

                if os.path.isfile(text_field) and text_field.endswith((".jpg", ".jpeg" ".png", ".tif")):
                    custom_image_name = os.path.basename(text_field)
                    custom_image_path = text_field
                else:
                    message_extra = " - WARNING - No custom image specified!"

            if custom_image_name and custom_image_path:
                copy_custom_image(custom_image_path, custom_image_name)

            # make sure the field is empty for next time
            bpy.context.window_manager.prop_grp.custom_image_name = ""

        elif self.image_mode == 'PLACEHOLDER_IMAGE':
            # Use the user_defined image
            directory = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', 'thumbnails'))
            custom_image_path = os.path.join(directory, "user_defined.png")

        elif self.image_mode == 'AUTO_RENDER':
            # Render the widget
            custom_image_name = self.widget_name + '.png'
            bpy.ops.bonewidget.render_widget_thumbnail(
                image_name=custom_image_name, use_blend_path=False)
            custom_image_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', 'custom_thumbnails'))

        message_type, return_message = add_remove_widgets(context, "add", bpy.types.WindowManager.widget_list.keywords['items'],
                                                          objects, self.widget_name, custom_image_name)

        if return_message:
            self.report({message_type}, return_message + message_extra)

        return {'FINISHED'}


class BONEWIDGET_OT_remove_widgets(bpy.types.Operator):
    """Remove selected widget object from the Bone Widget Library"""
    bl_idname = "bonewidget.remove_widgets"
    bl_label = "Remove Widgets"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        objects = bpy.context.window_manager.widget_list

        # try and remove the image - will abort if no custom image assigned or if missing
        remove_custom_image(get_widget_data(objects).get("image"))

        message_type, return_message = add_remove_widgets(
            context, "remove", bpy.types.WindowManager.widget_list.keywords['items'], objects)

        if return_message:
            self.report({message_type}, return_message)

        return {'FINISHED'}


class BONEWIDGET_OT_import_items_summary_popup(bpy.types.Operator):
    """Display summary of imported Items"""
    bl_idname = "bonewidget.import_summary_popup"
    bl_label = "Imported Item Summary"
    bl_options = {'INTERNAL'}

    def draw(self, context):
        layout = self.layout
        layout.scale_x = 1.2

        layout.separator()
        row = layout.row()

        if context.window_manager.custom_data.json_import_error:
            row.alert = True
            row.label(text=f"Error: Unsupported or damaged import file!")
            row.alert = False
            layout.separator()
        else:
            row.label(
                text=f"Imported Items: {context.window_manager.custom_data.imported()}")

            row = layout.row()
            row.label(
                text=f"Skipped Items: {context.window_manager.custom_data.skipped()}")

            row = layout.row()
            row.label(
                text=f"Failed Items: {context.window_manager.custom_data.failed()}")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        return {'FINISHED'}


def update_selected_options(self, context):
    wm = context.window_manager

    selected_values = []

    items = wm.prop_grp.import_item_data
    for i, item in enumerate(items):
        if self.select_all_items:
            selected_values.append(item.import_option)
            if item.import_option != "RENAME":
                item.import_option = "OVERWRITE"
        else:
            if i < len(BONEWIDGET_OT_import_items_ask_popup.selected_options_values):
                value = BONEWIDGET_OT_import_items_ask_popup.selected_options_values[i]
                if value != "RENAME":
                    item.import_option = value

    if self.select_all_items:
        # reset and store only once
        BONEWIDGET_OT_import_items_ask_popup.selected_options_values = selected_values


class BONEWIDGET_OT_import_items_ask_popup(bpy.types.Operator):
    """Ask user how to handle name collisions from the imported items"""
    bl_idname = "bonewidget.import_items_ask_popup"
    bl_label = "Imported Items"
    bl_options = {'INTERNAL'}

    import_options = get_import_options()

    select_all_items: BoolProperty(name="Select All", description="Will select all items to be added",
                                   default=False, update=update_selected_options)

    selected_options_values = []

    def draw(self, context):
        layout = self.layout
        layout.scale_x = 1.2

        # layout.separator()
        row = layout.row()
        row.label(text="Choose an action:")

        imported_items = context.window_manager.prop_grp.import_item_data

        for i, _ in enumerate(self.custom_import_data.skipped_imports):

            imported_item = imported_items[i]

            if self.custom_import_data.import_type == "widget":
                row = layout.row(align=True)
                row.scale_x = 2.0

                # Rename
                if imported_item.import_option == self.import_options[2][0]:
                    row.prop(imported_item, "name", text="")
                else:
                    row.label(text=str(imported_item.name))

                widget_name = self.custom_import_data.skipped_imports[i].name
                icon_id = context.window_manager.prop_grp.image_collection[widget_name].icon_id
                icon_row = row.row(align=True)
                icon_row.scale_x = 6
                icon_row.template_icon(icon_id, scale=1.4)

                row.separator(factor=0.4)
                row.prop(imported_item, "import_option", text="")

            elif self.custom_import_data.import_type == "colorset":
                row = layout.row(align=True)
                row.scale_x = 3.0

                # Rename
                if imported_item.import_option == self.import_options[2][0]:
                    row.prop(imported_item, "name", text="")
                else:
                    row.label(text=str(imported_item.name))

                row.separator(factor=0.4)

                # color sets
                color_set = context.window_manager.prop_grp.color_sets[i]
                split = row.split(factor=0.9)
                color_row = split.row(align=True)
                color_row.prop(color_set, "normal", text="")
                color_row.prop(color_set, "select", text="")
                color_row.prop(color_set, "active", text="")

                # options dropdown
                row.separator(factor=0.4)
                row.prop(imported_item, "import_option", text="")

        row = layout.row()
        row = layout.row()
        row = layout.row()

        row.prop(self, "select_all_items")

        layout.separator()

    def invoke(self, context, event):
        self.custom_import_data = bpy.context.window_manager.custom_data
        import_type = self.custom_import_data.import_type

        # make sure class values are empty
        BONEWIDGET_OT_import_items_ask_popup.selected_options_values = []

        # make sure the shared property group has a clean slate
        context.window_manager.prop_grp.color_sets.clear()
        context.window_manager.prop_grp.import_item_data.clear()
        context.window_manager.prop_grp.image_collection.clear()

        # generate the x number of drop down lists and widget names needed
        for n, widget in enumerate(self.custom_import_data.skipped_imports):

            # add new imported item
            import_item = context.window_manager.prop_grp.import_item_data.add()
            import_item.name = widget.name

            # add the color fields if the import is a color set
            if import_type == "colorset":
                color_instance = context.window_manager.prop_grp.color_sets.add()
                color_instance.name = widget.name
                color_instance.normal = widget.normal
                color_instance.select = widget.select
                color_instance.active = widget.active

            # widget preview images
            if import_type == "widget":
                image_path = os.path.join(
                    bpy.app.tempdir, "custom_thumbnails", widget.image)
                context.window_manager.prop_grp.image_collection.load(
                    widget.name, image_path, 'IMAGE')

        return context.window_manager.invoke_props_dialog(self, width=350)

    def execute(self, context):
        widget_results = {}
        widget_images = set()
        import_type = self.custom_import_data.import_type
        total_imports = len(self.custom_import_data.skipped_imports)

        for i, widget in enumerate(self.custom_import_data.skipped_imports[:]):
            imported_item = context.window_manager.prop_grp.import_item_data[i]

            action = imported_item.import_option

            if action == self.import_options[1][0]:  # skip
                continue

            new_widget_name = imported_item.name

            # error check before proceeding - widget renamed to empty string
            if widget.name != new_widget_name and new_widget_name.strip() == "":
                self.custom_import_data.failed_imports.update(widget)
                continue

            if import_type == "widget":
                widget_data = widget
                widget_image = widget.image
                # only append custom images
                widget_image = widget_image if widget_image != "user_defined.png" else ""

            elif import_type == "colorset":
                widget_data = context.window_manager.prop_grp.color_sets[i]
                widget_data = ColorSet.from_pg(
                    widget_data)  # convert to ColorSet class

            if action == self.import_options[0][0]:  # overwrite
                if import_type == "widget":
                    widget_results.update(widget_data.to_dict())
                    if widget_image:
                        widget_images.add(widget_image)

                elif import_type == "colorset":
                    # check if the import item name exists already and if it does, overwrite
                    color_set_list = context.window_manager.custom_color_presets
                    for index, item in enumerate(color_set_list):
                        if item.name == new_widget_name:
                            # Update the existing entry
                            item.normal = widget_data.normal
                            item.select = widget_data.select
                            item.active = widget_data.active
                            break
                    else:
                        widget_data.name = new_widget_name
                        add_color_set(context, widget_data)

            elif action == self.import_options[2][0]:  # Rename
                widget_data.name = new_widget_name
                if import_type == "widget":
                    # we need the dict version
                    widget_results.update(widget_data.to_dict())
                    if widget_image:
                        widget_images.add(widget_image)
                elif import_type == "colorset":
                    add_color_set(context, widget_data)

            # update the stats
            self.custom_import_data.new_imported_items += 1
            self.custom_import_data.skipped_imports.remove(widget)

        if import_type == "widget":
            update_widget_library(widget_results, widget_images,
                                  bpy.context.window_manager.prop_grp.import_library_filepath)

        # clear image collection if widgets were imported
        context.window_manager.prop_grp.image_collection.clear()

        # clear out all import item data
        context.window_manager.prop_grp.import_item_data.clear()

        # clear out all color sets
        context.window_manager.prop_grp.color_sets.clear()

        # del bpy.types.WindowManager.custom_data
        self.custom_import_data = None

        # reset previous selected options
        BONEWIDGET_OT_import_items_ask_popup.selected_options_values = []

        # display summary of imported widgets
        bpy.ops.bonewidget.import_summary_popup('INVOKE_DEFAULT')

        return {'FINISHED'}


class BONEWIDGET_OT_import_widget_library(bpy.types.Operator):
    """Import User Defined Widgets"""
    bl_idname = "bonewidget.import_widget_library"
    bl_label = "Import Library"
    bl_options = {'REGISTER'}

    filter_glob: StringProperty(
        default='*.zip',
        options={'HIDDEN'}
    )

    filename: StringProperty(
        name='Filename',
        subtype='FILE_NAME',
        description='Name of file to be imported',
    )

    filepath: StringProperty(
        subtype="FILE_PATH"
    )

    import_option: EnumProperty(
        name="Import Option",
        items=[
            ("OVERWRITE", "Overwrite", "Overwrite existing widget"),
            ("SKIP", "Skip", "Skip widget"),
            ("ASK", "Ask", "Ask user what to do")],
        default="ASK",
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.label(text="If duplicates are found:")
        row = layout.row(align=True)
        row.prop(self, "import_option", expand=True)

    def execute(self, context):
        if self.filepath and self.import_option:
            import_library_data = import_widget_library(
                self.filepath, self.import_option)
            setattr(BONEWIDGET_OT_shared_property_group,
                    "import_library_filepath", self.filepath)

            bpy.types.WindowManager.custom_data = import_library_data

            # if the number of failed widgets are equal to total imported widgets - call summary popup
            if import_library_data.failed() == import_library_data.total() or import_library_data.failed() == -1:
                import_library_data.reset_imports()
                bpy.ops.bonewidget.import_summary_popup('INVOKE_DEFAULT')

            elif self.import_option == "ASK":
                bpy.ops.bonewidget.import_items_ask_popup('INVOKE_DEFAULT')

            elif self.import_option in ["OVERWRITE", "SKIP"]:
                widget_images = set()
                widgets = {}

                # convert Widget objects to dict items and extract image names if any
                for widget in import_library_data.imported_items:
                    widgets.update(widget.to_dict())
                    widget_images.add(widget.image)

                update_widget_library(widgets, widget_images, self.filepath)

                bpy.ops.bonewidget.import_summary_popup('INVOKE_DEFAULT')

            else:
                bpy.ops.bonewidget.import_summary_popup('INVOKE_DEFAULT')

        return {'FINISHED'}

    def invoke(self, context, event):
        self.filename = ""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class BONEWIDGET_OT_export_widget_library(bpy.types.Operator):
    """Export User Defined Widgets"""
    bl_idname = "bonewidget.export_widget_library"
    bl_label = "Export Library"
    bl_options = {'REGISTER'}

    filter_glob: StringProperty(
        default='*.zip',
        options={'HIDDEN'}
    )

    filename: StringProperty(
        name='Filename',
        subtype='FILE_NAME',
        description='Name of file to be exported',
    )

    filepath: StringProperty(
        subtype="FILE_PATH"
    )

    def execute(self, context):
        if self.filepath and self.filename:
            num_widgets = export_widget_library(self.filepath)
            if num_widgets:
                self.report(
                    {'INFO'}, f"{num_widgets} user defined widgets exported successfully!")
            else:
                self.report({'INFO'}, "0 user defined widgets exported!")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filename = "widget_library.zip"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class BONEWIDGET_OT_toggle_collection_visibility(bpy.types.Operator):
    """Show/hide the bone widget collection"""
    bl_idname = "bonewidget.toggle_collection_visibilty"
    bl_label = "Collection Visibilty"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode == 'POSE')

    def execute(self, context):
        if not get_preferences(context).use_rigify_defaults:
            bw_collection_name = get_preferences(
                context).bonewidget_collection_name
        else:
            bw_collection_name = 'WGTS_' + context.active_object.name

        bw_collection = recursive_layer_collection(
            bpy.context.view_layer.layer_collection, bw_collection_name)
        bw_collection.hide_viewport = not bw_collection.hide_viewport
        # need to recursively search for the view_layer
        bw_collection.exclude = False
        return {'FINISHED'}


class BONEWIDGET_OT_delete_unused_widgets(bpy.types.Operator):
    """Delete unused objects in the WGT collection"""
    bl_idname = "bonewidget.delete_unused_widgets"
    bl_label = "Delete Unused Widgets"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode == 'POSE')

    def execute(self, context):
        try:
            delete_unused_widgets()
        except:
            self.report(
                {'INFO'}, "Can't find the Widget Collection. Does it exist?")
        return {'FINISHED'}


class BONEWIDGET_OT_clear_bone_widgets(bpy.types.Operator):
    """Clears widgets from selected pose bones but doesn't remove them from the scene"""
    bl_idname = "bonewidget.clear_widgets"
    bl_label = "Clear Widgets"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode == 'POSE')

    def execute(self, context):
        clear_bone_widgets()
        return {'FINISHED'}


class BONEWIDGET_OT_resync_widget_names(bpy.types.Operator):
    """Clear widgets from selected pose bones"""
    bl_idname = "bonewidget.resync_widget_names"
    bl_label = "Resync Widget Names"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode == 'POSE')

    def execute(self, context):
        resync_widget_names()
        return {'FINISHED'}


class BONEWIDGET_OT_add_object_as_widget(bpy.types.Operator):
    """Add selected object as widget for active bone"""
    bl_idname = "bonewidget.add_as_widget"
    bl_label = "Confirm selected Object as widget shape"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) == 2 and context.object.mode == 'POSE')

    def execute(self, context):
        add_object_as_widget(context, get_collection(context))
        return {'FINISHED'}


class BONEWIDGET_OT_reset_default_images(bpy.types.Operator):
    """Resets the thumbnails for all default widgets"""
    bl_idname = "bonewidget.reset_default_images"
    bl_label = "Reset"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        reset_default_images()
        return {'FINISHED'}


class BONEWIDGET_OT_user_data_filebrowser(bpy.types.Operator):
    """Select Location for Custom User Data"""
    bl_idname = "bonewidget.user_data_filebrowser"
    bl_label = "Select Location"
    bl_options = {'INTERNAL'}

    directory: StringProperty(
        name="User Data Directory",
        description="Choose a directory to store user data",
        subtype='DIR_PATH'
    )

    def execute(self, context):
        get_preferences(context).user_data_location = self.directory
        # self.report({'INFO'}, f"User data path set to: {self.directory}")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class BONEWIDGET_OT_set_bone_color(bpy.types.Operator):
    """Add bone color to selected widgets"""
    bl_idname = "bonewidget.set_bone_color"
    bl_label = "Set Bone Color to Widget"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode in ['POSE', 'EDIT'] and
            (context.selected_bones or context.selected_pose_bones))

    def execute(self, context):
        set_bone_color(context, context.scene.bw_settings.bone_widget_colors)
        return {'FINISHED'}


class BONEWIDGET_OT_clear_bone_color(bpy.types.Operator):
    """Add bone color to selected widgets"""
    bl_idname = "bonewidget.clear_bone_color"
    bl_label = "Clear Bone Color"
    bl_description = (
        "Clear Bone Color from selected bones.\n"
        "(Note: Blender will show Edit Bone color in Pose Mode if Pose Bone color is default)"
    )

    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode in ['POSE', 'EDIT'] and
            (context.selected_bones or context.selected_pose_bones))

    def execute(self, context):
        set_bone_color(context, "DEFAULT", get_preferences(
            context).clear_both_modes)
        return {'FINISHED'}


class BONEWIDGET_OT_copy_bone_color(bpy.types.Operator):
    """Copy the colors of the active bone to the custom colors above (ignores default colors)"""
    bl_idname = "bonewidget.copy_bone_color"
    bl_label = "Copy Bone Color"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        bones = context.selected_pose_bones if context.object.mode == 'POSE' else context.selected_bones
        return (context.object and context.object.type == 'ARMATURE'
                and context.object.mode in ['POSE', 'EDIT'] and len(bones) == 1)

    def execute(self, context):
        if context.object.mode == 'POSE':
            selected_bone = context.selected_pose_bones[0]
            if not selected_bone.color.is_custom and not 'THEME' in selected_bone.color.palette:
                selected_bone = context.active_bone
            copy_bone_color(context, selected_bone)
        elif context.object.mode == 'EDIT':
            copy_bone_color(context, context.selected_bones[0])
        return {'FINISHED'}


class BONEWIDGET_OT_add_color_set_from(bpy.types.Operator):
    """Adds a color set to presets from selected Theme or from custom palette"""
    bl_idname = "bonewidget.add_color_set_from"
    bl_label = "Add color set to presets"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.object and
            context.object.type == 'ARMATURE' and
            (
                (context.object.mode == 'POSE' and context.selected_pose_bones) or
                (context.object.mode == 'EDIT' and context.selected_editable_bones and get_preferences(
                    context).edit_bone_colors != 'DEFAULT')
            )
        )

    def execute(self, context):

        base_name = "Color Set"
        new_name = base_name
        count = 1

        while any(item.name == new_name for item in context.window_manager.custom_color_presets):
            new_name = f"{base_name}.{count:03d}"
            count += 1

        new_item = context.window_manager.custom_color_presets.add()

        if context.scene.bw_settings.bone_widget_colors == "CUSTOM":
            # add item from custom color palette

            new_item.name = new_name
            if context.object.mode == 'POSE':
                new_item.normal = context.scene.bw_settings.custom_pose_color_set.normal
                new_item.select = context.scene.bw_settings.custom_pose_color_set.select
                new_item.active = context.scene.bw_settings.custom_pose_color_set.active

            elif context.object.mode == "EDIT" and \
                    get_preferences(context).edit_bone_colors != 'DEFAULT':  # edit mode colors if turned on in preferences

                new_item.normal = context.scene.bw_settings.custom_edit_color_set.normal
                new_item.select = context.scene.bw_settings.custom_edit_color_set.select
                new_item.active = context.scene.bw_settings.custom_edit_color_set.active

        elif "THEME" in context.scene.bw_settings.bone_widget_colors:
            # add item from selected theme

            theme = context.scene.bw_settings.bone_widget_colors
            theme_id = int(theme[-2:]) - 1
            theme_color_set = bpy.context.preferences.themes[0].bone_color_sets[theme_id]

            new_item.name = theme
            new_item.normal = theme_color_set.normal
            new_item.select = theme_color_set.select
            new_item.active = theme_color_set.active

        # save_color_sets(context)
        return {'FINISHED'}


class BONEWIDGET_OT_add_default_colorset(bpy.types.Operator):
    """Adds a default color set to presets"""
    bl_idname = "bonewidget.add_default_custom_colorset"
    bl_label = "Add a default color set"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        add_color_set(context)
        return {'FINISHED'}


class BONEWIDGET_OT_add_colorset_to_bone(bpy.types.Operator):
    """Adds a bone color set to selected bones"""
    bl_idname = "bonewidget.add_colorset_to_bone"
    bl_label = "Apply selected color set to selected bones - mode sensitive"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.object:
            bones = context.selected_pose_bones if context.object.mode == 'POSE' else context.selected_bones
            return (context.object.type == 'ARMATURE'
                    and context.object.mode in ['POSE', 'EDIT'] and len(bones) >= 1) \
                and not (context.object.mode == "EDIT"
                         and get_preferences(context).edit_bone_colors == 'DEFAULT')

    def execute(self, context):
        if context.object.mode == "EDIT" and \
                get_preferences(context).edit_bone_colors != 'DEFAULT':
            selected_bones = context.selected_bones
        elif context.object.mode == "POSE":
            selected_bones = context.selected_pose_bones
        else:
            return {'CANCELLED'}

        if selected_bones:
            for bone in selected_bones:

                bone.color.palette = "CUSTOM"

                index = context.window_manager.colorset_list_index
                item = context.window_manager.custom_color_presets[index]

                bone.color.custom.normal = item.normal
                bone.color.custom.select = item.select
                bone.color.custom.active = item.active

        return {'FINISHED'}


class BONEWIDGET_OT_remove_item(bpy.types.Operator):
    """Removes selected color set from the preset list"""
    bl_idname = "bonewidget.remove_custom_item"
    bl_label = "Remove Selected Color Set"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.colorset_list_index >= 0 and not context.scene.bw_settings.lock_colorset_color_changes

    def execute(self, context):
        my_list = context.window_manager.custom_color_presets
        index = context.window_manager.colorset_list_index
        my_list.remove(index)
        context.window_manager.colorset_list_index = min(
            max(0, index - 1), len(my_list) - 1)
        save_color_sets(context)
        return {'FINISHED'}


class BONEWIDGET_OT_lock_custom_colorset_changes(bpy.types.Operator):
    """Locks/Unlocks the ability to save changes to color set items"""
    bl_idname = "bonewidget.lock_custom_colorset_changes"
    bl_label = "Lock/Unlock changes to color set presets"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        context.scene.bw_settings.lock_colorset_color_changes = not context.scene.bw_settings.lock_colorset_color_changes
        return {'FINISHED'}


class BONEWIDGET_OT_move_custom_item_up(bpy.types.Operator):
    """Moves the selected color set up in the list"""
    bl_idname = "bonewidget.move_custom_item_up"
    bl_label = "Move Custom Item Up"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        wm = context.window_manager
        idx = wm.colorset_list_index

        if idx > 0:
            wm.custom_color_presets.move(idx, idx - 1)
            wm.colorset_list_index -= 1

            save_color_sets(context)

        return {'FINISHED'}


class BONEWIDGET_OT_move_custom_item_down(bpy.types.Operator):
    """Moves the selected color set down in the list"""
    bl_idname = "bonewidget.move_custom_item_down"
    bl_label = "Move Custom Item Down"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        wm = context.window_manager
        idx = wm.colorset_list_index

        if idx < len(wm.custom_color_presets) - 1:
            wm.custom_color_presets.move(idx, idx + 1)
            wm.colorset_list_index += 1

            save_color_sets(context)

        return {'FINISHED'}


class BONEWIDGET_OT_add_preset_from_bone(bpy.types.Operator):
    """Adds new preset from the active bone's color palette"""
    bl_idname = "bonewidget.add_preset_from_bone"
    bl_label = "Add Preset from active Bone"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return (
            context.object and
            context.object.type == 'ARMATURE' and
            (
                (context.object.mode == 'POSE' and context.selected_pose_bones) or
                (context.object.mode == 'EDIT' and context.selected_editable_bones and get_preferences(
                    context).edit_bone_colors != 'DEFAULT')
            )
        )

    def execute(self, context):
        base_name = "Color Set"
        new_name = base_name
        count = 1

        bone = context.active_pose_bone if context.object.mode == 'POSE' else context.active_bone

        # do some validation checking
        if bone.color.palette == 'DEFAULT':
            mode = "pose mode" if context.object.mode == 'POSE' else "edit mode"
            self.report(
                {'WARNING'}, f"No available color set found in {mode}!")
            return {'CANCELLED'}

        existing_names = {
            item.name for item in context.window_manager.custom_color_presets}
        while new_name in existing_names:
            new_name = f"{base_name}.{count:03d}"
            count += 1

        new_item = context.window_manager.custom_color_presets.add()

        if bone.color.is_custom:
            # add item from custom color palette of active bone
            new_item.name = new_name
            new_item.normal = bone.color.custom.normal
            new_item.select = bone.color.custom.select
            new_item.active = bone.color.custom.active

        elif "THEME" in bone.color.palette:
            # add item from selected theme of active bone
            theme = bone.color.palette
            theme_id = int(theme[-2:]) - 1
            theme_color_set = bpy.context.preferences.themes[0].bone_color_sets[theme_id]

            new_item.name = theme
            new_item.normal = theme_color_set.normal
            new_item.select = theme_color_set.select
            new_item.active = theme_color_set.active

        # save_color_sets(context)
        return {'FINISHED'}


class BONEWIDGET_OT_add_presets_from_armature(bpy.types.Operator):
    """Adds new presets from the active bone's color palette"""
    bl_idname = "bonewidget.add_presets_from_armature"
    bl_label = "Add Preset from selected Armature"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return (
            context.object and
            context.object.type == 'ARMATURE' and
            (
                (context.object.mode == 'POSE' and context.selected_pose_bones) or
                (context.object.mode == 'EDIT' and context.selected_editable_bones and get_preferences(
                    context).edit_bone_colors != 'DEFAULT')
            )
        )

    def execute(self, context):
        armature = context.object.data

        colorset_imports = scan_armature_color_presets(context, armature)

        if colorset_imports.skipped_imports:
            bpy.types.WindowManager.custom_data = colorset_imports

            bpy.ops.bonewidget.import_items_ask_popup('INVOKE_DEFAULT')
        else:
            self.report({'INFO'}, f"No new custom color sets found!")

        return {'FINISHED'}


class BONEWIDGET_OT_import_color_presets(bpy.types.Operator):
    """Import User Defined Color Presets"""
    bl_idname = "bonewidget.import_color_presets"
    bl_label = "Import Color Presets"
    bl_options = {'REGISTER'}

    filter_glob: StringProperty(
        default='*.zip',
        options={'HIDDEN'}
    )

    filename: StringProperty(
        name='Filename',
        subtype='FILE_NAME',
        description='Name of file to be imported',
    )

    filepath: StringProperty(
        subtype="FILE_PATH"
    )

    import_option: EnumProperty(
        name="Import Option",
        items=[
            ("OVERWRITE", "Overwrite", "Overwrite existing preset"),
            ("SKIP", "Skip", "Skip preset"),
            ("ASK", "Ask", "Ask user what to do")],
        default="ASK",
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.label(text="If duplicates are found:")
        row = layout.row(align=True)
        row.prop(self, "import_option", expand=True)

    def execute(self, context):
        if self.filepath and self.import_option:
            import_preset_data = import_color_presets(
                self.filepath, self.import_option)
            bpy.context.window_manager.prop_grp.import_library_filepath = self.filepath

            bpy.types.WindowManager.custom_data = import_preset_data

            # if the number of failed presets are equal to total imported presets - call summary popup
            if import_preset_data.failed() == import_preset_data.total():
                import_preset_data.reset_imports()
                bpy.ops.bonewidget.import_summary_popup('INVOKE_DEFAULT')

            elif self.import_option == "ASK":
                bpy.ops.bonewidget.import_items_ask_popup('INVOKE_DEFAULT')

            elif self.import_option in ["OVERWRITE", "SKIP"]:
                update_color_presets(
                    import_preset_data.imported_items, self.filepath)

                bpy.ops.bonewidget.import_summary_popup('INVOKE_DEFAULT')
            else:
                bpy.ops.bonewidget.import_summary_popup('INVOKE_DEFAULT')

        return {'FINISHED'}

    def invoke(self, context, event):
        self.filename = ""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class BONEWIDGET_OT_export_color_presets(bpy.types.Operator):
    """Export User Defined Color Presets"""
    bl_idname = "bonewidget.export_color_presets"
    bl_label = "Export Color Presets"
    bl_options = {'REGISTER'}

    filter_glob: StringProperty(
        default='*.zip',
        options={'HIDDEN'}
    )

    filename: StringProperty(
        name='Filename',
        subtype='FILE_NAME',
        description='Name of file to be exported',
    )

    filepath: StringProperty(
        subtype="FILE_PATH"
    )

    def execute(self, context):
        if self.filepath and self.filename:
            num_presets = export_color_presets(self.filepath, context)
            if num_presets:
                self.report(
                    {'INFO'}, f"{num_presets} color presets exported successfully!")
            else:
                self.report({'INFO'}, "0 color presets exported!")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filename = "color_presets.zip"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class BONEWIDGET_OT_render_widget_thumbnail(bpy.types.Operator):
    """Render a wireframe thumbnail of the active object"""
    bl_idname = "bonewidget.render_widget_thumbnail"
    bl_label = "Render Widget Thumbnail"
    bl_options = {'REGISTER', 'UNDO'}

    image_name: StringProperty(
        name="Image Name",
        default=""
    )
    wire_frame_color: FloatVectorProperty(
        name="Wireframe Color",
        subtype='COLOR',
        size=4,
        default=(1, 1, 1, 1),
        min=0.0,
        max=1.0
    )
    wire_frame_thickness: FloatProperty(
        name="Wireframe Thickness",
        default=0.5,
        min=0.01,
        max=2.0
    )
    use_object_color: BoolProperty(
        name="Use Object Color",
        default=False
    )
    use_blend_path: BoolProperty(
        name="Save to Current Directory",
        default=True
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH'

    def invoke(self, context, event):
        # Set the image name to the active object
        if context.active_object:
            self.image_name = context.active_object.name + "_thumbnail"
        else:
            self.image_name = "widget_thumbnail"
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "use_object_color", text="Use Object Color")

        if not self.use_object_color:
            row = layout.row()
            split = row.split(factor=0.6)
            split.label(text="Wireframe Color:")
            split.prop(self, "wire_frame_color", text="")
        row = layout.row()
        split = row.split(factor=0.6)
        split.label(text="Wireframe Thickness:")
        split.prop(self, "wire_frame_thickness", text="")

    def execute(self, context):
        active_obj = context.view_layer.objects.active
        if not active_obj:
            self.report({'WARNING'}, "No active object found.")
            return {'CANCELLED'}

        widget_obj = create_wireframe_copy(
            active_obj,
            self.use_object_color,
            self.wire_frame_color,
            self.wire_frame_thickness
        )

        # store the current view perspective
        original_view_perspective = context.space_data.region_3d.view_perspective

        original_scene = context.scene
        new_scene = bpy.data.scenes.new("BoneWidget_Thumbnail")
        new_scene.collection.objects.link(widget_obj)
        context.window.scene = new_scene

        viewport_area = next(
            (a for a in context.window.screen.areas if a.type == 'VIEW_3D'), None)
        if not viewport_area:
            self.report({'WARNING'}, "No 3D Viewport found.")
            return {'CANCELLED'}

        original_view_matrix = setup_viewport(context)
        new_camera = add_camera_from_view(context)

        destination_path = render_widget_thumbnail(
            self.image_name, widget_obj, image_directory=self.use_blend_path)

        restore_viewport_position(
            context, original_view_matrix, original_view_perspective)

        context.window.scene = original_scene

        # Clean up (widget and camera objs and data)
        widget_data = widget_obj.data
        camera_data = new_camera.data

        bpy.data.objects.remove(widget_obj, do_unlink=True)
        bpy.data.meshes.remove(widget_data)

        bpy.data.objects.remove(new_camera, do_unlink=True)
        bpy.data.cameras.remove(camera_data)

        # Remove Scene
        bpy.data.scenes.remove(new_scene)

        if self.use_blend_path:
            self.report({'INFO'}, "Thumbnail saved at: " + destination_path)

        return {'FINISHED'}


classes = (
    BONEWIDGET_OT_remove_widgets,
    BONEWIDGET_OT_add_widgets,
    BONEWIDGET_OT_import_widget_library,
    BONEWIDGET_OT_export_widget_library,
    BONEWIDGET_OT_match_symmetrize_shape,
    BONEWIDGET_OT_match_bone_transforms,
    BONEWIDGET_OT_return_to_armature,
    BONEWIDGET_OT_edit_widget,
    BONEWIDGET_OT_create_widget,
    BONEWIDGET_OT_toggle_collection_visibility,
    BONEWIDGET_OT_delete_unused_widgets,
    BONEWIDGET_OT_clear_bone_widgets,
    BONEWIDGET_OT_resync_widget_names,
    BONEWIDGET_OT_add_object_as_widget,
    BONEWIDGET_OT_import_items_summary_popup,
    BONEWIDGET_OT_import_items_ask_popup,
    BONEWIDGET_OT_shared_property_group,
    BONEWIDGET_OT_image_select,
    BONEWIDGET_OT_add_custom_image,
    BONEWIDGET_OT_reset_default_images,
    BONEWIDGET_OT_user_data_filebrowser,
    BONEWIDGET_OT_set_bone_color,
    BONEWIDGET_OT_clear_bone_color,
    BONEWIDGET_OT_copy_bone_color,
    BONEWIDGET_OT_add_color_set_from,
    BONEWIDGET_OT_add_default_colorset,
    BONEWIDGET_OT_add_colorset_to_bone,
    BONEWIDGET_OT_remove_item,
    BONEWIDGET_OT_lock_custom_colorset_changes,
    BONEWIDGET_OT_move_custom_item_up,
    BONEWIDGET_OT_move_custom_item_down,
    BONEWIDGET_OT_add_preset_from_bone,
    BONEWIDGET_OT_add_presets_from_armature,
    BONEWIDGET_OT_import_color_presets,
    BONEWIDGET_OT_export_color_presets,
    BONEWIDGET_OT_render_widget_thumbnail,
)


def register():
    bpy.utils.register_class(ImportColorSet)
    bpy.utils.register_class(ImportItemData)

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.WindowManager.prop_grp = bpy.props.PointerProperty(
        type=BONEWIDGET_OT_shared_property_group)


def unregister():
    del bpy.types.WindowManager.prop_grp

    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

    unregister_class(ImportColorSet)
    unregister_class(ImportItemData)
