import bpy
import bpy.utils.previews
from .jsonFunctions import readWidgets, getWidgetData, get_addon_dir, JSON_USER_WIDGETS
import os
from .. import __package__
from mathutils import Vector

preview_collections = {}


def createPreviewCollection():
    if preview_collections:
        del bpy.types.WindowManager.widget_list
        for pcoll in preview_collections.values():
            bpy.utils.previews.remove(pcoll)
        preview_collections.clear()

    pcoll = bpy.utils.previews.new()
    pcoll.widget_list = ()
    preview_collections["widgets"] = pcoll

    bpy.types.WindowManager.widget_list = bpy.props.EnumProperty(
        items=generate_previews(), name="Shape", description="Shape", update=preview_update
    )


def generate_previews():
    enum_items = []

    pcoll = preview_collections["widgets"]
    if pcoll.widget_list:
        return pcoll.widget_list
    
    directory = os.path.abspath(os.path.join(get_addon_dir(), '..', 'thumbnails'))
    custom_directory = os.path.abspath(os.path.join(get_addon_dir(), '..', 'custom_thumbnails'))

    if directory and os.path.exists(directory):
        widget_data = {item[0]: item[1].get("image", "missing_image.png") for item in readWidgets().items()}
        widget_names = sorted(widget_data.keys())

        for i, name in enumerate(widget_names):
            image = widget_data.get(name, "")
            if image is not None:
                filepath = os.path.join(directory, image)

            # try in custom_thumbnails if above failed
            if not os.path.exists(filepath):
                filepath = os.path.join(custom_directory, image)

            # if image still not found, let the user know
            if not os.path.exists(filepath):
                filepath = os.path.join(directory, "missing_image.png")

            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
                
            face_data_info = "Contains Face Data" if getWidgetData(name).get("faces") else ""
            enum_items.append((name, name, face_data_info, thumb.icon_id, i))
    
    pcoll.widget_list = enum_items
    return enum_items


def preview_update(self, context):
    generate_previews()


def get_preview_default():
    return bpy.context.preferences.addons[__package__].preferences.preview_default


def copyCustomImage(filepath, filename):
    if os.path.exists(filepath):
        image_directory = os.path.abspath(os.path.join(get_addon_dir(), '..', 'custom_thumbnails'))
        destination_path = os.path.join(image_directory, filename)

        try:
            # create custom thumbnail folder if not existing
            if not os.path.exists(image_directory):
                os.makedirs(image_directory)

            import shutil
            shutil.copyfile(filepath, destination_path)
            return True
        except:
            pass
    return False


def removeCustomImage(filename):
    image_directory = os.path.abspath(os.path.join(get_addon_dir(), '..', 'custom_thumbnails'))
    destination_path = os.path.join(image_directory, filename)
    
    if os.path.isfile(destination_path):
        # make sure the image is only used once - else stop
        count = 0
        for v in readWidgets(JSON_USER_WIDGETS).values():
            if v.get("image") == filename:
                count += 1
            if count > 1:
                return False
            
        try:
            os.remove(destination_path)
            return True
        except:
            pass
    return False


#### Thumbnail Render Functions ####
def create_wireframe_copy(obj, use_color, color, thickness):
    copy = obj.copy()
    copy.data = obj.data.copy()
    if not use_color:
        copy.color = color

    # Create a new Geometry Nodes modifier
    geo_mod = copy.modifiers.new(name="BoneWidget_WireFrame", type='NODES')

    # Create a new node group and assign it to the modifier
    node_group = bpy.data.node_groups.new(name="BONEWIDGET_GeometryGroup", type='GeometryNodeTree')
    geo_mod.node_group = node_group

    # Add input and output sockets
    node_group.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    node_group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")

    # Add Thickness input
    thickness_socket = node_group.interface.new_socket(name="Thickness", in_out="INPUT", socket_type="NodeSocketFloat")
    thickness_socket.default_value = 0.05
    thickness_socket.min_value = 0.01
    thickness_socket.max_value = 1

    # Create nodes
    node_input = node_group.nodes.new('NodeGroupInput')
    node_output = node_group.nodes.new('NodeGroupOutput')
    node_uv_sphere = node_group.nodes.new('GeometryNodeMeshUVSphere')
    node_mesh_to_curve = node_group.nodes.new('GeometryNodeMeshToCurve')
    node_curve_circle = node_group.nodes.new('GeometryNodeCurvePrimitiveCircle')
    node_instance_on_points = node_group.nodes.new('GeometryNodeInstanceOnPoints')
    node_curve_to_mesh = node_group.nodes.new('GeometryNodeCurveToMesh')
    node_join_geometry = node_group.nodes.new('GeometryNodeJoinGeometry')

    # Set initial values (internal)
    node_uv_sphere.inputs["Segments"].default_value = 8
    node_uv_sphere.inputs["Rings"].default_value = 8
    node_curve_circle.inputs["Resolution"].default_value = 8

    # Position nodes for better visualization (optional)
    node_input.location = (-400, 0)
    node_uv_sphere.location = (-150, 100)
    node_mesh_to_curve.location = (-150, -50)
    node_curve_circle.location = (-150, -150)
    node_instance_on_points.location = (100,250)
    node_curve_to_mesh.location = (100, -100)
    node_join_geometry.location = (350, 0)
    node_output.location = (550, 0)

    # Connect nodes
    node_group.links.new(node_input.outputs["Geometry"], node_instance_on_points.inputs["Points"])
    node_group.links.new(node_input.outputs["Geometry"], node_mesh_to_curve.inputs["Mesh"])
    node_group.links.new(node_input.outputs["Thickness"], node_uv_sphere.inputs["Radius"])
    node_group.links.new(node_input.outputs["Thickness"], node_curve_circle.inputs["Radius"])
    node_group.links.new(node_uv_sphere.outputs["Mesh"], node_instance_on_points.inputs["Instance"])
    node_group.links.new(node_mesh_to_curve.outputs["Curve"], node_curve_to_mesh.inputs["Curve"])
    node_group.links.new(node_curve_circle.outputs["Curve"], node_curve_to_mesh.inputs["Profile Curve"])
    node_group.links.new(node_instance_on_points.outputs["Instances"], node_join_geometry.inputs["Geometry"])
    node_group.links.new(node_curve_to_mesh.outputs["Mesh"], node_join_geometry.inputs["Geometry"])
    node_group.links.new(node_join_geometry.outputs["Geometry"], node_output.inputs["Geometry"])
    
    geo_mod["Socket_2"] = thickness

    return copy


def setup_viewport(context):
    area = context.area
    space = context.space_data
    region_3d = space.region_3d
    original_view_matrix = region_3d.view_matrix.copy()

    bpy.ops.view3d.view_selected()

    return original_view_matrix


def restore_viewport_position(context, view_matrix, view_perspective):
    if context.space_data.type == 'VIEW_3D':
        region_3d = context.space_data.region_3d

        # Restore viewport matrix position
        region_3d.view_matrix = view_matrix

        # Restore viewport perspective
        region_3d.view_perspective = view_perspective


def render_widget_thumbnail(image_name, widget_object, image_directory):
    if image_directory: # If True save to the current directory but...
        if bpy.data.filepath: # Check the file has been saved
            image_directory = os.path.dirname(bpy.data.filepath)
        else:
            image_directory = os.path.expanduser("~") # Fall back if it hasn't been daved
        # add '.png' to the name
        image_name = image_name + '.png'
        
    else: # if False use the add-on location
        image_directory = os.path.abspath(os.path.join(get_addon_dir(), '..', 'custom_thumbnails'))

    destination_path = os.path.join(image_directory, image_name)

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x, scene.render.resolution_y = (512, 512)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.view_settings.view_transform = 'Standard'
    scene.render.film_transparent = True
    scene.display.shading.light = 'FLAT'
    scene.display.shading.color_type = 'OBJECT'
    scene.render.filepath = image_directory

    # Reframe Camera
    camera = scene.camera
    obj = widget_object
    frame_object_with_padding(camera, obj, padding=0.1)

    bpy.ops.render.render(write_still=False)
    bpy.data.images['Render Result'].save_render(filepath=bpy.path.abspath(destination_path))

    return bpy.path.abspath(destination_path)


def add_camera_from_view(context):
    name = "BoneWidget_Thumbnail_Camera"

    region_3d = context.region_data
    space = context.space_data

    if region_3d is None or space.type != 'VIEW_3D':
        print("This must be run from a 3D Viewport.")
        return None

    # Create camera data and object
    cam_data = bpy.data.cameras.new(name)
    cam_obj = bpy.data.objects.new(name, cam_data)
    context.scene.collection.objects.link(cam_obj)

    # Align camera to current viewport
    cam_obj.matrix_world = region_3d.view_matrix.inverted()

    # Make it the active camera
    context.scene.camera = cam_obj

    return cam_obj


def frame_object_with_padding(camera, obj, padding=0.1):
    depsgraph = bpy.context.evaluated_depsgraph_get()

    # Get bounding box corners in world space
    coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    # Find center of bounding box
    center = sum(coords, Vector()) / len(coords)

    # Scale each point away from the center to apply padding
    scaled_coords = [(center + (co - center) * (1 + padding)) for co in coords]

    # Flatten the list of Vectors into a list of floats
    flat_coords = [v for co in scaled_coords for v in co]

    # Use the camera fitting function
    cam_location, _ = camera.camera_fit_coords(depsgraph, flat_coords)
    camera.location = cam_location
