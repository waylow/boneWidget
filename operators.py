import bpy

from .functions import (
    findMatchBones,
    fromWidgetFindBone,
    symmetrizeWidget_helper,
    boneMatrix,
    createWidget,
    editWidget,
    returnToArmature,
    addRemoveWidgets,
    readWidgets,
    getCollection,
    getViewLayerCollection,
    recurLayerCollection,
    deleteUnusedWidgets,
    clearBoneWidgets,
    resyncWidgetNames,
    addObjectAsWidget,
    importWidgetLibrary,
    exportWidgetLibrary,
    createPreviewCollection,
)

from bpy.props import FloatProperty, BoolProperty, FloatVectorProperty, StringProperty


def advanced_options_toggled(self, context):
    if self.advanced_options:
        self.global_size_advanced = (self.global_size_simple,) * 3
        self.slide_advanced[1] = self.slide_simple
    else:
        self.global_size_simple = self.global_size_advanced[1]
        self.slide_simple = self.slide_advanced[1]


class BONEWIDGET_OT_createWidget(bpy.types.Operator):
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

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        row = col.row(align=True)
        row.prop(self, "relative_size")
        row = col.row(align=True)
        row.prop(self, "global_size_advanced" if self.advanced_options else "global_size_simple", expand=False)
        row = col.row(align=True)
        row.prop(self, "slide_advanced" if self.advanced_options else "slide_simple", text="Slide")
        row = col.row(align=True)
        row.prop(self, "rotation", text="Rotation")
        row = col.row(align=True)
        row.prop(self, "advanced_options")

    def execute(self, context):
        wgts = readWidgets()
        slide = self.slide_advanced if self.advanced_options else (0.0, self.slide_simple, 0.0)
        global_size = self.global_size_advanced if self.advanced_options else (self.global_size_simple,) * 3
        for bone in bpy.context.selected_pose_bones:
            createWidget(bone, wgts[context.window_manager.widget_list], self.relative_size, global_size, [
                         1, 1, 1], slide, self.rotation, getCollection(context))
        return {'FINISHED'}


class BONEWIDGET_OT_editWidget(bpy.types.Operator):
    """Edit the widget for selected bone"""
    bl_idname = "bonewidget.edit_widget"
    bl_label = "Edit"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode == 'POSE'
                and context.active_pose_bone.custom_shape is not None)

    def execute(self, context):
        active_bone = context.active_pose_bone
        try:
            editWidget(active_bone)
        except KeyError:
            self.report({'INFO'}, 'This widget is the Widget Collection')
        return {'FINISHED'}


class BONEWIDGET_OT_returnToArmature(bpy.types.Operator):
    """Switch back to the armature"""
    bl_idname = "bonewidget.return_to_armature"
    bl_label = "Return to armature"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'MESH'
                and context.object.mode in ['EDIT', 'OBJECT'])

    def execute(self, context):
        b = bpy.context.object
        if fromWidgetFindBone(bpy.context.object):
            returnToArmature(bpy.context.object)
        else:
            self.report({'INFO'}, 'Object is not a bone widget')
        return {'FINISHED'}


class BONEWIDGET_OT_matchBoneTransforms(bpy.types.Operator):
    """Match the widget to the bone transforms"""
    bl_idname = "bonewidget.match_bone_transforms"
    bl_label = "Match bone transforms"

    def execute(self, context):
        if bpy.context.mode == "POSE":
            for bone in bpy.context.selected_pose_bones:
                boneMatrix(bone.custom_shape, bone)

        else:
            for ob in bpy.context.selected_objects:
                if ob.type == 'MESH':
                    matchBone = fromWidgetFindBone(ob)
                    if matchBone:
                        boneMatrix(ob, matchBone)
        return {'FINISHED'}


class BONEWIDGET_OT_matchSymmetrizeShape(bpy.types.Operator):
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
        collection = getViewLayerCollection(context, widget)
        widgetsAndBones = findMatchBones()[0]
        activeObject = findMatchBones()[1]
        widgetsAndBones = findMatchBones()[0]

        if not activeObject:
            self.report({"INFO"}, "No active bone or object")
            return {'FINISHED'}

        for bone in widgetsAndBones:
            symmetrizeWidget_helper(bone, collection, activeObject, widgetsAndBones)

        return {'FINISHED'}


class BONEWIDGET_OT_addWidgets(bpy.types.Operator):
    """Add selected mesh object to Bone Widget Library"""
    bl_idname = "bonewidget.add_widgets"
    bl_label = "Add New Widget to Library"


    widget_name: StringProperty(
        name="Widget Name",
        default="",
        description="The name of the new widget",
        options={"TEXTEDIT_UPDATE"},
    )


    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'MESH' and context.object.mode == 'OBJECT'
                and context.active_object is not None)


    def draw(self, context):
        layout = self.layout
        layout.label(text="Widget Name:")
        layout.prop(self, "widget_name", text="")


    def invoke(self, context, event):
        if bpy.context.selected_objects:
            self.widget_name = context.active_object.name
            return context.window_manager.invoke_props_dialog(self) #title="Add New Widget to Library")
            
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
        message_type, return_message = addRemoveWidgets(context, "add", bpy.types.WindowManager.widget_list.keywords['items'], objects, self.widget_name)

        if return_message:
            self.report({message_type}, return_message)

        return {'FINISHED'}


class BONEWIDGET_OT_removeWidgets(bpy.types.Operator):
    """Remove selected widget object from the Bone Widget Library"""
    bl_idname = "bonewidget.remove_widgets"
    bl_label = "Remove Widgets"

    def execute(self, context):
        objects = bpy.context.window_manager.widget_list
        message_type, return_message = addRemoveWidgets(context, "remove", bpy.types.WindowManager.widget_list.keywords['items'], objects)

        if return_message:
            self.report({message_type}, return_message)
            
        return {'FINISHED'}


class BONEWIDGET_OT_importLibrary(bpy.types.Operator):
    """Import User Defined Widgets"""
    bl_idname = "bonewidget.import_library"
    bl_label = "Import Library"


    filter_glob: StringProperty(
        default='*.bwl',
        options={'HIDDEN'}
    )

    filename: StringProperty(
        name='Filename',
        description='Name of file to be imported',
    )

    filepath: StringProperty(
        subtype="FILE_PATH"
    )

    def execute(self, context):
        if self.filepath:
            num_widgets, failed_imports = importWidgetLibrary(self.filepath)

            if failed_imports:
                failed = " | ".join(failed_imports)
                message = f"{num_widgets} widgets imported. {len(failed_imports)} failed: {failed}"
            else:
                message = f"{num_widgets} widgets imported successfully!"
                
            self.report({'INFO'}, message)

            # trigger an update and display the new widgets if any widgets were imported
            if num_widgets:
                createPreviewCollection()
            
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filename = ""
        context.window_manager.fileselect_add(self)        
        return {'RUNNING_MODAL'}


class BONEWIDGET_OT_exportLibrary(bpy.types.Operator):
    """Export User Defined Widgets"""
    bl_idname = "bonewidget.export_library"
    bl_label = "Export Library"


    filter_glob: StringProperty(
        default='*.bwl',
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
        if self.filepath:
            num_widgets = exportWidgetLibrary(self.filepath)
            self.report({'INFO'}, f"{num_widgets} widgets exported successfully!")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.filename = "widgetLibrary.bwl"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class BONEWIDGET_OT_toggleCollectionVisibility(bpy.types.Operator):
    """Show/hide the bone widget collection"""
    bl_idname = "bonewidget.toggle_collection_visibilty"
    bl_label = "Collection Visibilty"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode == 'POSE')

    def execute(self, context):
        if not context.preferences.addons[__package__].preferences.use_rigify_defaults:
            bw_collection_name = context.preferences.addons[__package__].preferences.bonewidget_collection_name
        else:
            bw_collection_name = 'WGTS_' + context.active_object.name

        bw_collection = recurLayerCollection(bpy.context.view_layer.layer_collection, bw_collection_name)
        bw_collection.hide_viewport = not bw_collection.hide_viewport
        #need to recursivly search for the view_layer
        bw_collection.exclude = False
        return {'FINISHED'}


class BONEWIDGET_OT_deleteUnusedWidgets(bpy.types.Operator):
    """Delete unused objects in the WGT collection"""
    bl_idname = "bonewidget.delete_unused_widgets"
    bl_label = "Delete Unused Widgets"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode == 'POSE')

    def execute(self, context):
        try:
            deleteUnusedWidgets()
        except:
            self.report({'INFO'}, "Can't find the Widget Collection. Does it exist?")
        return {'FINISHED'}


class BONEWIDGET_OT_clearBoneWidgets(bpy.types.Operator):
    """Clears widgets from selected pose bones but doesn't remove them from the scene."""
    bl_idname = "bonewidget.clear_widgets"
    bl_label = "Clear Widgets"

    @classmethod
    def poll(cls, context):
         return (context.object and context.object.type == 'ARMATURE' and context.object.mode == 'POSE')

    def execute(self, context):
        clearBoneWidgets()
        return {'FINISHED'}


class BONEWIDGET_OT_resyncWidgetNames(bpy.types.Operator):
    """Clear widgets from selected pose bones"""
    bl_idname = "bonewidget.resync_widget_names"
    bl_label = "Resync Widget Names"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE' and context.object.mode == 'POSE')

    def execute(self, context):
        resyncWidgetNames()
        return {'FINISHED'}


class BONEWIDGET_OT_addObjectAsWidget(bpy.types.Operator):
    """Add selected object as widget for active bone."""
    bl_idname = "bonewidget.add_as_widget"
    bl_label = "Confirm selected Object as widget shape"

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) == 2 and context.object.mode == 'POSE')

    def execute(self, context):
        addObjectAsWidget(context, getCollection(context))
        return {'FINISHED'}

classes = (
    BONEWIDGET_OT_removeWidgets,
    BONEWIDGET_OT_addWidgets,
    BONEWIDGET_OT_importLibrary,
    BONEWIDGET_OT_exportLibrary,
    BONEWIDGET_OT_matchSymmetrizeShape,
    BONEWIDGET_OT_matchBoneTransforms,
    BONEWIDGET_OT_returnToArmature,
    BONEWIDGET_OT_editWidget,
    BONEWIDGET_OT_createWidget,
    BONEWIDGET_OT_toggleCollectionVisibility,
    BONEWIDGET_OT_deleteUnusedWidgets,
    BONEWIDGET_OT_clearBoneWidgets,
    BONEWIDGET_OT_resyncWidgetNames,
    BONEWIDGET_OT_addObjectAsWidget,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

