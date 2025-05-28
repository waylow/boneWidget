import bpy
import threading
from .functions import save_color_sets, update_bone_color

save_timer = None

def debounce_save(context):
    global save_timer
    if save_timer is not None:
        save_timer.cancel()
    save_timer = threading.Timer(2.0, save_color_sets, args=[context])
    save_timer.start()


class PresetColorSetItem(bpy.types.PropertyGroup):

    def update_colorset_list(self, context):
        if not context.scene.turn_off_colorset_save and not context.scene.lock_colorset_color_changes:
            debounce_save(context)

    name: bpy.props.StringProperty(name="Name", default="Untitled", update=update_colorset_list)
    normal: bpy.props.FloatVectorProperty(
        name="Normal",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for the surface of bones",
        update=update_colorset_list,
    )
    select: bpy.props.FloatVectorProperty(
        name="Select",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for selected bones",
        update=update_colorset_list,
    )
    active: bpy.props.FloatVectorProperty(
        name="Active",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for active bones",
        update=update_colorset_list,
    )


class CustomColorSet(bpy.types.PropertyGroup):

    normal: bpy.props.FloatVectorProperty(
        name="Normal",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for the surface of bones",
        update=update_bone_color,
    )

    select: bpy.props.FloatVectorProperty(
        name="Select",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for selected bones",
        update=update_bone_color,
    )

    active: bpy.props.FloatVectorProperty(
        name="Active",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for active bones",
        update=update_bone_color,
    )
