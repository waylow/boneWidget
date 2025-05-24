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
    copy_edit_bone_color,
    bone_color_items,
    get_preferences,
    save_color_sets,
    load_color_presets,
    create_wireframe_copy,
    setup_viewport,
    restore_viewport_position,
    render_widget_thumbnail,
    add_camera_from_view,
    frame_object_with_padding,
)

from bpy.props import FloatProperty, BoolProperty, FloatVectorProperty, IntVectorProperty, StringProperty, EnumProperty


class BONEWIDGET_OT_shared_property_group(bpy.types.PropertyGroup):
    """Storage class for Shared Attribute Properties"""
    
    custom_image_data = ("", "")
    import_library_filepath = ""


class BONEWIDGET_OT_create_widget(bpy.types.Operator):
    """Creates a widget for selected bone"""
    bl_idname = "bonewidget.create_widget"
    bl_label = "Create"
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
        soft_max = 10,
        description="Set the thickness of a wireframe widget"
    )

    bone_color: EnumProperty(
        name="Bone Color",
        description="Color of bone widget",
        items=bone_color_items,
        default=0,
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
        row.prop(self, "global_size_advanced" if self.advanced_options else "global_size_simple", expand=False)
        row = col.row(align=True)
        row.prop(self, "slide_advanced" if self.advanced_options else "slide_simple", text="Slide")
        row = col.row(align=True)
        row.prop(self, "rotation", text="Rotation")
        row = col.row(align=True)
        if bpy.app.version >= (4,2,0):
            row.prop(self, "wireframe_width", text="Wire Width")
            row = col.row(align=True)
            if self.advanced_options:
                row.prop(self, "bone_color")
                row = col.row(align=True)
        row.prop(self, "advanced_options")

    def execute(self, context):
        widget_data = get_widget_data(context.window_manager.widget_list)
        slide = self.slide_advanced if self.advanced_options else (0.0, self.slide_simple, 0.0)
        global_size = self.global_size_advanced if self.advanced_options else (self.global_size_simple,) * 3
        bone_color = self.bone_color if self.advanced_options else "DEFAULT"
        for bone in bpy.context.selected_pose_bones:
            create_widget(bone, widget_data, self.relative_size, global_size, slide, self.rotation,
                         get_collection(context), self.use_face_data, self.wireframe_width, bone_color)
        return {'FINISHED'}


class BONEWIDGET_OT_edit_widget(bpy.types.Operator):
    """Edit the widget for selected bone"""
    bl_idname = "bonewidget.edit_widget"
    bl_label = "Edit"

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

    def execute(self, context):
        if bpy.context.mode == "POSE":
            for bone in bpy.context.selected_pose_bones:
                match_bone_matrix(bone.custom_shape, bone)

        else:
            for ob in bpy.context.selected_objects:
                if ob.type == 'MESH':
                    matchBone = from_widget_find_bone(ob)
                    if matchBone:
                        match_bone_matrix(ob, matchBone)
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
        widgetsAndBones = find_match_bones()[0]
        activeObject = find_match_bones()[1]
        widgetsAndBones = find_match_bones()[0]

        if not activeObject:
            self.report({"INFO"}, "No active bone or object")
            return {'FINISHED'}

        for bone in widgetsAndBones:
            symmetrize_widget_helper(bone, collection, activeObject, widgetsAndBones)

        return {'FINISHED'}


class BONEWIDGET_OT_image_select(bpy.types.Operator):
    """Open a Fileselect browser and get the image location"""
    bl_idname = "bonewidget.image_select"
    bl_label = "Select Image"


    filter_glob: StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;',
        options={'HIDDEN'}
    )
    
    filename: StringProperty(
        name='Filename',
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
        setattr(BONEWIDGET_OT_shared_property_group, "custom_image_data", (self.filepath, self.filename))
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
    bl_options = {'REGISTER', 'UNDO'}


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
                if bpy.app.version >= (4,1,0):
                    row.prop(bpy.context.window_manager.prop_grp, "custom_image_name", text="", placeholder="Choose an image...", icon="FILE_IMAGE")
                else:
                    row.prop(bpy.context.window_manager.prop_grp, "custom_image_name", text="", icon="FILE_IMAGE")
                row.operator('bonewidget.image_select', icon='FILEBROWSER', text="")

    def invoke(self, context, event):
        if bpy.context.selected_objects:
            self.widget_name = context.active_object.name
            setattr(BONEWIDGET_OT_shared_property_group, "custom_image_name", StringProperty(name="Image Name"))
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
            custom_image_path, custom_image_name = bpy.context.window_manager.prop_grp.custom_image_data #context.window_manager.custom_image

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

            bpy.context.window_manager.prop_grp.custom_image_name = ""  # make sure the field is empty for next time


        elif self.image_mode == 'PLACEHOLDER_IMAGE':
            # Use the user_defined image
            directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'thumbnails'))
            custom_image_path = os.path.join(directory, "user_defined.png")


        elif self.image_mode == 'AUTO_RENDER':
            # Render the widget
            custom_image_name = self.widget_name + '.png'
            bpy.ops.bonewidget.render_widget_thumbnail(image_name=custom_image_name, use_blend_path=False)
            custom_image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'custom_thumbnails'))
            

        message_type, return_message = add_remove_widgets(context, "add", bpy.types.WindowManager.widget_list.keywords['items'],
                                                        objects, self.widget_name, custom_image_name)

        if return_message:
            self.report({message_type}, return_message + message_extra)

        return {'FINISHED'}


class BONEWIDGET_OT_remove_widgets(bpy.types.Operator):
    """Remove selected widget object from the Bone Widget Library"""
    bl_idname = "bonewidget.remove_widgets"
    bl_label = "Remove Widgets"

    def execute(self, context):
        objects = bpy.context.window_manager.widget_list

        # try and remove the image - will abort if no custom image assigned or if missing
        remove_custom_image(get_widget_data(objects).get("image"))
        
        message_type, return_message = add_remove_widgets(context, "remove", bpy.types.WindowManager.widget_list.keywords['items'], objects)

        if return_message:
            self.report({message_type}, return_message)
            
        return {'FINISHED'}


class BONEWIDGET_OT_import_widgets_summary_popup(bpy.types.Operator):
    """Display summary of imported Widget Library"""
    bl_idname = "bonewidget.widget_summary_popup"
    bl_label = "Imported Widget Summary"

 
    def draw(self, context):
        layout = self.layout
        layout.scale_x = 1.2

        layout.separator()
        row = layout.row()
        row.label(text=f"Imported Widgets: {context.window_manager.custom_data.new_widgets}")

        row = layout.row()
        row.label(text=f"Skipped Widgets: {context.window_manager.custom_data.skipped()}")
        
        row = layout.row()
        row.label(text=f"Failed Widgets: {context.window_manager.custom_data.failed()}")


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        return {'FINISHED'}


class BONEWIDGET_OT_import_widgets_ask_popup(bpy.types.Operator):
    """Ask user how to handle name collisions from the imported Widget Library"""
    bl_idname = "bonewidget.widget_ask_popup"
    bl_label = "Imported Widget Choice Popup"

    widgetImportData = None

    import_options = [
        ("OVERWRITE", "Overwrite", "Overwrite existing widget"),
        ("SKIP", "Skip", "Skip widget"),
        ("RENAME", "Rename", "Rename widget"),
    ]

    def draw(self, context):
        layout = self.layout
        layout.scale_x = 1.2

        layout.separator()
        row = layout.row()
        row.label(text="Choose an action:")

        row = layout.row()
        for i, _ in enumerate(self.widgetImportData.skipped_widgets):
            if getattr(context.window_manager.prop_grp, f"ImportOptions{i}") == self.import_options[2][0]: # Rename
                row.prop(context.window_manager.prop_grp, f"EditName{i}", text="")
            else:
                row.label(text=str(getattr(context.window_manager.prop_grp, f"EditName{i}")))
            row.prop(context.window_manager.prop_grp, f"ImportOptions{i}", text=" ")
            row = layout.row()

    def invoke(self, context, event):
        self.widgetImportData = bpy.context.window_manager.custom_data
        
        # generate the x number of drop down lists and widget names needed
        for n, widget in enumerate(self.widgetImportData.skipped_widgets):
            widget_name = next(iter(widget.keys()))
            setattr(BONEWIDGET_OT_shared_property_group, f"ImportOptions{n}", EnumProperty(
                    name=f"ImportOptions{n}",
                    description="Choose an option",
                    items=self.import_options,
                    default="SKIP"
            ))
            setattr(bpy.context.window_manager.prop_grp, f"ImportOptions{n}", "SKIP")
            
            setattr(BONEWIDGET_OT_shared_property_group, f"EditName{n}", StringProperty(
                    name=f"EditName{n}",
                    default=widget_name,
                    description="The name of the widget",
            ))
            setattr(bpy.context.window_manager.prop_grp, f"EditName{n}", widget_name)
        
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        widget_results = {}
        widget_images = set()

        for i, widget in enumerate(self.widgetImportData.skipped_widgets):
            widget_name, widget_data = next(iter(widget.items()))
            widget_image = widget_data.get('image')
            widget_image = widget_image if widget_image != "user_defined.png" else ""  # only append custom images
            action = getattr(bpy.context.window_manager.prop_grp, f"ImportOptions{i}")
            new_widget_name = getattr(bpy.context.window_manager.prop_grp, f"EditName{i}")

            # error check before proceeding - widget renamed to empty string
            if widget_name != new_widget_name and new_widget_name.strip() == "":
                self.widgetImportData.failed_widgets.update(widget)
                continue

            if action == self.import_options[0][0]: # overwrite
                widget_results.update(widget)
                if widget_image: widget_images.add(widget_image)
                self.widgetImportData.new_widgets += 1
                self.widgetImportData.skipped_widgets.remove(widget)
            elif action == self.import_options[2][0]: # Rename
                widget_results.update({new_widget_name: widget_data})
                if widget_image: widget_images.add(widget_image)
                self.widgetImportData.new_widgets += 1
                self.widgetImportData.skipped_widgets.remove(widget)
                
        update_widget_library(widget_results, widget_images, bpy.context.window_manager.prop_grp.import_library_filepath)

        # clean up the data from the property group
        for i in range(self.widgetImportData.skipped()):
            delattr(BONEWIDGET_OT_shared_property_group, f"ImportOptions{i}")
            delattr(BONEWIDGET_OT_shared_property_group, f"EditName{i}")

        #del bpy.types.WindowManager.custom_data
        self.widgetImportData = None

        # display summary of imported widgets
        bpy.ops.bonewidget.widget_summary_popup('INVOKE_DEFAULT')

        return {'FINISHED'}


class BONEWIDGET_OT_import_library(bpy.types.Operator):
    """Import User Defined Widgets"""
    bl_idname = "bonewidget.import_library"
    bl_label = "Import Library"


    filter_glob: StringProperty(
        default='*.zip',
        options={'HIDDEN'}
    )

    filename: StringProperty(
        name='Filename',
        description='Name of file to be imported',
    )

    filepath: StringProperty(
        subtype="FILE_PATH"
    )

    import_option : EnumProperty(
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
            import_libraryData = import_widget_library(self.filepath, self.import_option)
            bpy.context.window_manager.prop_grp.import_library_filepath = self.filepath

            bpy.types.WindowManager.custom_data = import_libraryData

            if self.import_option == "ASK":
                bpy.types.WindowManager.custom_data = import_libraryData
                bpy.ops.bonewidget.widget_ask_popup('INVOKE_DEFAULT')

            elif self.import_option == "OVERWRITE" or self.import_option == "SKIP":
                widget_images = set()

                # extract image names if any
                for _, value in import_libraryData.widgets.items():
                    widget_images.add(value['image'])

                update_widget_library(import_libraryData.widgets, widget_images, self.filepath)

                bpy.ops.bonewidget.widget_summary_popup('INVOKE_DEFAULT')
            else:
                bpy.ops.bonewidget.widget_summary_popup('INVOKE_DEFAULT')
            
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filename = ""
        context.window_manager.fileselect_add(self)        
        return {'RUNNING_MODAL'}


class BONEWIDGET_OT_export_library(bpy.types.Operator):
    """Export User Defined Widgets"""
    bl_idname = "bonewidget.export_library"
    bl_label = "Export Library"


    filter_glob: StringProperty(
        default='*.zip',
        options={'HIDDEN'}
    )
    
    filename: StringProperty(
        name='Filename',
        description='Name of file to be exported',
    )

    filepath: StringProperty(
        subtype="FILE_PATH"
    )

    def execute(self, context):
        if self.filepath and self.filename:
            num_widgets = export_widget_library(self.filepath)
            self.report({'INFO'}, f"{num_widgets} user defined widgets exported successfully!")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filename = "widgetLibrary.zip"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class BONEWIDGET_OT_toggle_collection_visibility(bpy.types.Operator):
    """Show/hide the bone widget collection"""
    bl_idname = "bonewidget.toggle_collection_visibilty"
    bl_label = "Collection Visibilty"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode == 'POSE')

    def execute(self, context):
        if not get_preferences(context).use_rigify_defaults:
            bw_collection_name = get_preferences(context).bonewidget_collection_name
        else:
            bw_collection_name = 'WGTS_' + context.active_object.name

        bw_collection = recursive_layer_collection(bpy.context.view_layer.layer_collection, bw_collection_name)
        bw_collection.hide_viewport = not bw_collection.hide_viewport
        #need to recursivly search for the view_layer
        bw_collection.exclude = False
        return {'FINISHED'}


class BONEWIDGET_OT_delete_unused_widgets(bpy.types.Operator):
    """Delete unused objects in the WGT collection"""
    bl_idname = "bonewidget.delete_unused_widgets"
    bl_label = "Delete Unused Widgets"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode == 'POSE')

    def execute(self, context):
        try:
            delete_unused_widgets()
        except:
            self.report({'INFO'}, "Can't find the Widget Collection. Does it exist?")
        return {'FINISHED'}


class BONEWIDGET_OT_clear_bone_widgets(bpy.types.Operator):
    """Clears widgets from selected pose bones but doesn't remove them from the scene"""
    bl_idname = "bonewidget.clear_widgets"
    bl_label = "Clear Widgets"

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

    def execute(self, context):
        reset_default_images()
        return {'FINISHED'}


class BONEWIDGET_OT_set_bone_color(bpy.types.Operator):
    """Add bone color to selected widgets"""
    bl_idname = "bonewidget.set_bone_color"
    bl_label = "Set Bone Color to Widget"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode in ['POSE', 'EDIT'])

    def execute(self, context):
        set_bone_color(context, context.scene.bone_widget_colors)
        return {'FINISHED'}


class BONEWIDGET_OT_clear_bone_color(bpy.types.Operator):
    """Add bone color to selected widgets"""
    bl_idname = "bonewidget.clear_bone_color"
    bl_label = "Clear Bone Color"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode in ['POSE', 'EDIT'])

    def execute(self, context):
        set_bone_color(context, "DEFAULT")
        return {'FINISHED'}


class BONEWIDGET_OT_copy_bone_color(bpy.types.Operator):
    """Copy the colors of the active bone to the custom colors above (ignores default colors)"""
    bl_idname = "bonewidget.copy_bone_color"
    bl_label = "Copy Bone Color"

    @classmethod
    def poll(cls, context):
        bones = context.selected_pose_bones if context.object.mode == 'POSE' else context.selected_bones
        return (context.object and context.object.type == 'ARMATURE'
                and context.object.mode in ['POSE', 'EDIT'] and len(bones) == 1)

    def execute(self, context):
        if context.object.mode == 'POSE':
            copy_bone_color(context, context.selected_pose_bones[0]) #changed
        elif context.object.mode == 'EDIT':
            copy_edit_bone_color(context, context.selected_bones[0])
        return {'FINISHED'}


class BONEWIDGET_OT_add_color_set_from(bpy.types.Operator):
    """Adds a color set to presets from selected Theme or from custom palette"""
    bl_idname = "bonewidget.add_color_set_from"
    bl_label = "Add color set to presets"


    def execute(self, context):

        base_name = "Color Set"
        new_name = base_name
        count = 1

        while any(item.name == new_name for item in context.window_manager.custom_color_presets):
            new_name = f"{base_name}.{count:03d}"
            count += 1

        new_item = context.window_manager.custom_color_presets.add()

        if context.scene.bone_widget_colors == "CUSTOM":
            # add item from custom color palette

            new_item.name = new_name
            if context.object.mode == 'POSE':
                new_item.normal = context.scene.custom_pose_color_set.normal
                new_item.select = context.scene.custom_pose_color_set.select
                new_item.active = context.scene.custom_pose_color_set.active
                
            elif context.object.mode == "EDIT" and \
                 get_preferences(context).edit_bone_colors == True: # edit mode colors if turned on in preferences
                
                new_item.normal = context.scene.custom_edit_color_set.normal
                new_item.select = context.scene.custom_edit_color_set.select
                new_item.active = context.scene.custom_edit_color_set.active

        elif "THEME" in context.scene.bone_widget_colors:
            # add item from selected theme

            theme = context.scene.bone_widget_colors
            theme_id = int(theme[-2:]) - 1
            theme_color_set = bpy.context.preferences.themes[0].bone_color_sets[theme_id]

            new_item.name = theme
            new_item.normal = theme_color_set.normal
            new_item.select = theme_color_set.select
            new_item.active = theme_color_set.active

        save_color_sets(context)
        return {'FINISHED'}
    

class BONEWIDGET_OT_add_default_colorset(bpy.types.Operator):
    """Adds a default color set to presets"""
    bl_idname = "bonewidget.add_default_custom_colorset"
    bl_label = "Add a default color set"

    def execute(self, context):
        new_item = context.window_manager.custom_color_presets.add()
        base_name = "Color Set"
        new_name = base_name
        count = 1

        while any(item.name == new_name for item in context.window_manager.custom_color_presets):
            new_name = f"{base_name}.{count:03d}"
            count += 1

        new_item.name = new_name
        new_item.normal = (1.0, 0.0, 0.0)
        new_item.select = (0.0, 1.0, 0.0)
        new_item.active = (0.0, 0.0, 1.0)
        
        save_color_sets(context)

        return {'FINISHED'}
    

class BONEWIDGET_OT_add_colorset_to_bone(bpy.types.Operator):
    """Adds a bone color set to selected bones"""
    bl_idname = "bonewidget.add_colorset_to_bone"
    bl_label = "Apply selected color set to selected bones - mode sensitive"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        bones = context.selected_pose_bones if context.object.mode == 'POSE' else context.selected_bones
        return (context.object and context.object.type == 'ARMATURE'
                and context.object.mode in ['POSE', 'EDIT'] and len(bones) >= 1) \
                and not (context.object.mode == "EDIT"
                        and get_preferences(context).edit_bone_colors == False)

    def execute(self, context):
        if context.object.mode == "EDIT" and \
                 get_preferences(context).edit_bone_colors == True: 
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

    @classmethod
    def poll(cls, context):
        return context.window_manager.colorset_list_index >= 0 and not context.scene.lock_colorset_color_changes

    def execute(self, context):
        my_list = context.window_manager.custom_color_presets
        index = context.window_manager.colorset_list_index
        my_list.remove(index)
        context.window_manager.colorset_list_index = min(max(0, index - 1), len(my_list) - 1)
        save_color_sets(context)
        return {'FINISHED'}
    

class BONEWIDGET_OT_lock_custom_colorset_changes(bpy.types.Operator):
    """Locks/Unlocks the ability to save changes to color set items"""
    bl_idname = "bonewidget.lock_custom_colorset_changes"
    bl_label = "Lock/Unlock changes to color set presets"

    def execute(self, context):
        context.scene.lock_colorset_color_changes = not context.scene.lock_colorset_color_changes
        return {'FINISHED'}
    

class BONEWIDGET_OT_reload_colorset_items(bpy.types.Operator):
    """Refreshes the custom colorset list from disk"""
    bl_idname = "bonewidget.reload_colorset_items"
    bl_label = "Refresh the bone color set presets"

    def execute(self, context):
        context.window_manager.custom_color_presets.clear()
        load_color_presets(context)
        return {'FINISHED'}


class BONEWIDGET_OT_move_custom_item_up(bpy.types.Operator):
    """Moves the selected color set up in the list"""
    bl_idname = "bonewidget.move_custom_item_up"
    bl_label = "Move Custom Item Up"

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

    def execute(self, context):
        wm = context.window_manager
        idx = wm.colorset_list_index

        if idx < len(wm.custom_color_presets) - 1:
            wm.custom_color_presets.move(idx, idx + 1)
            wm.colorset_list_index += 1

            save_color_sets(context)

        return {'FINISHED'}


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

        viewport_area = next((a for a in context.window.screen.areas if a.type == 'VIEW_3D'), None)
        if not viewport_area:
            self.report({'WARNING'}, "No 3D Viewport found.")
            return {'CANCELLED'}

        original_view_matrix = setup_viewport(context)
        new_camera = add_camera_from_view(context)

        destination_path = render_widget_thumbnail(self.image_name, widget_obj, image_directory=self.use_blend_path)

        restore_viewport_position(context, original_view_matrix, original_view_perspective)

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
    BONEWIDGET_OT_import_library,
    BONEWIDGET_OT_export_library,
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
    BONEWIDGET_OT_import_widgets_summary_popup,
    BONEWIDGET_OT_import_widgets_ask_popup,
    BONEWIDGET_OT_shared_property_group,
    BONEWIDGET_OT_image_select,
    BONEWIDGET_OT_add_custom_image,
    BONEWIDGET_OT_reset_default_images,
    BONEWIDGET_OT_set_bone_color,
    BONEWIDGET_OT_clear_bone_color,
    BONEWIDGET_OT_copy_bone_color,
    BONEWIDGET_OT_add_color_set_from,
    BONEWIDGET_OT_add_default_colorset,
    BONEWIDGET_OT_add_colorset_to_bone,
    BONEWIDGET_OT_remove_item,
    BONEWIDGET_OT_lock_custom_colorset_changes,
    BONEWIDGET_OT_reload_colorset_items,
    BONEWIDGET_OT_move_custom_item_up,
    BONEWIDGET_OT_move_custom_item_down,
    BONEWIDGET_OT_render_widget_thumbnail,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.WindowManager.prop_grp = bpy.props.PointerProperty(type=BONEWIDGET_OT_shared_property_group)


def unregister():
    del bpy.types.WindowManager.prop_grp
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

