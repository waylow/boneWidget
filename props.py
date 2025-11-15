import bpy
from .functions import (
    update_bone_color,
    bone_color_items_short,
    live_update_toggle
)
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty, PointerProperty


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


class BW_Settings(PropertyGroup):
    live_update_on: BoolProperty(
        name="Live Update On",
        description="Enable live widget updates",
        default=False
    )
    live_update_toggle: BoolProperty(
        name="Live Update Toggle",
        description="Toggle live updates in the UI",
        default=False,
        update=live_update_toggle,
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
    # Blender's bone color themes
    bone_widget_colors: EnumProperty(
        name="Colors",
        description="Select a Bone Color",
        items=bone_color_items_short,  # get the themes minus the blank ones
        default=1,  # THEME01
    )

    # Nested Property Groups
    custom_edit_color_set: PointerProperty(type=CustomColorSet)
    custom_pose_color_set: PointerProperty(type=CustomColorSet)


save_timer = None


def debounce_save(context):
    """Schedule saving the color sets 1 second after the last change."""
    from .functions import save_color_sets
    global save_timer

    if save_timer is not None:
        try:
            bpy.app.timers.unregister(save_timer)
        except ValueError:
            pass

    def delayed_save():
        save_color_sets(context)
        return None  # stop the timer

    save_timer = delayed_save
    bpy.app.timers.register(save_timer, first_interval=1.0)


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
    bpy.utils.register_class(CustomColorSet)
    bpy.utils.register_class(BW_Settings)
    bpy.types.Scene.bw_settings = bpy.props.PointerProperty(type=BW_Settings)



def unregister():
    del bpy.types.Scene.bw_settings
    bpy.utils.unregister_class(BW_Settings)
    bpy.utils.unregister_class(CustomColorSet)
