import bpy
import threading
from .functions import update_bone_color
from bpy.types import PropertyGroup
from bpy.props import BoolProperty


class BW_Settings(PropertyGroup):
    live_update_on: BoolProperty(
        name="Live Update On",
        description="Enable live widget updates",
        default=True
    )
    live_update_toggle: BoolProperty(
        name="Live Update Toggle",
        description="Toggle live updates in the UI",
        default=False
    )
    turn_off_colorset_save: BoolProperty(
        name="Turn Off ColorSet Save",
        description="Disable automatic saving of color sets",
        default=False
    )
    lock_colorset_color_changes: BoolProperty(
        name="Lock ColorSet Color Changes",
        description="Prevent modifying the current color set",
        default=False
    )


save_timer = None


def debounce_save(context):
    # moved here to avoid circular dependencies
    from .functions import save_color_sets
    global save_timer
    if save_timer is not None:
        save_timer.cancel()
    save_timer = threading.Timer(2.0, save_color_sets, args=[context])
    save_timer.start()


class PresetColorSetItem(bpy.types.PropertyGroup):

    def update_colorset_list(self, context):
        if not context.scene.bw_settings.turn_off_colorset_save and not context.scene.bw_settings.lock_colorset_color_changes:
            debounce_save(context)

    name: bpy.props.StringProperty(
        name="Name", default="Untitled", update=update_colorset_list)
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

    name: bpy.props.StringProperty(name="Name", default="Untitled")

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


class ImportColorSet(bpy.types.PropertyGroup):

    normal: bpy.props.FloatVectorProperty(
        name="Normal",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for the surface of bones",
    )

    select: bpy.props.FloatVectorProperty(
        name="Select",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for selected bones",
    )

    active: bpy.props.FloatVectorProperty(
        name="Active",
        subtype='COLOR_GAMMA',
        default=(0.0, 0.0, 0.0),
        size=3,
        min=0.0, max=1.0,
        description="Color used for active bones",
    )


def get_import_options():
    return [
        ("OVERWRITE", "Add/Overwrite", "Add or Overwrite existing item"),
        ("SKIP", "Skip", "Skip item"),
        ("RENAME", "Rename", "Rename item"),
    ]


class ImportItemData(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(
        name="Unnamed",
        description="The name of the imported item"
    )

    import_option: bpy.props.EnumProperty(
        name="Options",
        description="Choose an option",
        items=get_import_options(),
        default="SKIP"
    )


def register():
    bpy.utils.register_class(BW_Settings)
    bpy.types.Scene.bw_settings = bpy.props.PointerProperty(type=BW_Settings)


def unregister():
    del bpy.types.Scene.bw_settings
    bpy.utils.unregister_class(BW_Settings)
