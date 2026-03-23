import bpy
from .functions.main_functions import (
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


# CloudRig Spine: Cartoon 形状参数枚举
CLOUDRIG_SPINE_TOON_ITEMS = [
    ('NONE', "None", "Standard Bone Widget behavior"),
    ('SHAPE_IK', "IK Shape", "Update spine_toon.shape_ik"),
    ('SHAPE_IK_SECONDARY', "IK Secondary", "Update spine_toon.shape_ik_secondary"),
    ('SHAPE_TORSO', "Torso", "Update spine_toon.shape_torso"),
    ('SHAPE_FK', "FK Shape", "Update fk_chain.shape_fk"),
    ('SHAPE_FK_ROOT', "FK Root Shape", "Update fk_chain.shape_fk_root"),
]

# CloudRig Limb: Biped Leg 形状参数枚举
CLOUDRIG_LIMB_LEG_ITEMS = [
    ('NONE', "None", "Standard Bone Widget behavior"),
    ('LEG_STRETCH', "Stretch Shape", "Update chain.shape_stretch"),
    ('LEG_STRETCH_ENDS', "Stretch Ends", "Update chain.shape_stretch_ends"),
    ('LEG_FK', "FK Shape", "Update fk_chain.shape_fk"),
    ('LEG_FK_ROOT', "FK Root Shape", "Update fk_chain.shape_fk_root"),
    ('LEG_IK_MASTER', "IK Master", "Update ik_chain.shape_ik_master"),
    ('LEG_IK_FIRST', "First IK", "Update ik_chain.shape_ik_first"),
    ('LEG_IK_POLE', "IK Pole", "Update ik_chain.shape_pole"),
    ('LEG_FOOT_ROLL', "Foot Roll", "Update leg.shape_footroll"),
]

# CloudRig Spine: IK/FK 形状参数枚举
CLOUDRIG_SPINE_IKFK_ITEMS = [
    ('NONE', "None", "Standard Bone Widget behavior"),
    ('SHAPE_HIP', "Hip", "Update spine.shape_hip"),
    ('SHAPE_CHEST', "Chest", "Update spine.shape_chest"),
    ('SHAPE_TORSO', "Torso", "Update spine.shape_torso"),
    ('SHAPE_IK', "IK Shape", "Update spine.shape_ik"),
]

# CloudRig Chain: FK 形状参数枚举
CLOUDRIG_CHAIN_FK_ITEMS = [
    ('NONE', "None", "Standard Bone Widget behavior"),
    ('FK_SHAPE', "FK Shape", "Update fk_chain.shape_fk"),
    ('FK_ROOT_SHAPE', "FK Root Shape", "Update fk_chain.shape_fk_root"),
]

# CloudRig Chain: IK 形状参数枚举
CLOUDRIG_CHAIN_IK_ITEMS = [
    ('NONE', "None", "Standard Bone Widget behavior"),
    ('IK_MASTER', "IK Master", "Update ik_chain.shape_ik_master"),
    ('IK_FIRST', "First IK", "Update ik_chain.shape_ik_first"),
    ('IK_POLE', "IK Pole", "Update ik_chain.shape_pole"),
]

# CloudRig Chain: Toon 形状参数枚举
CLOUDRIG_CHAIN_TOON_ITEMS = [
    ('NONE', "None", "Standard Bone Widget behavior"),
    ('CHAIN_STRETCH', "Stretch Shape", "Update chain.shape_stretch"),
    ('CHAIN_STRETCH_ENDS', "Stretch Ends", "Update chain.shape_stretch_ends"),
    ('CHAIN_DEF_CONTROL', "Def Control", "Update chain.shape_def_control"),
]

# CloudRig Aim 形状参数枚举
CLOUDRIG_AIM_ITEMS = [
    ('NONE', "None", "Standard Bone Widget behavior"),
    ('AIM_TARGET', "Target", "Update aim.shape_target"),
    ('AIM_EYE', "Eye", "Update aim.shape_eye"),
    ('AIM_ROOT', "Root", "Update aim.shape_root"),
    ('AIM_HIGHLIGHT', "Highlight", "Update aim.shape_highlight"),
    ('AIM_MASTER', "Master", "Update aim.shape_master"),
]

# CloudRig Single Control 形状参数枚举
CLOUDRIG_SINGLE_CONTROL_ITEMS = [
    ('NONE', "None", "Standard Bone Widget behavior"),
    ('CONTROL_SHAPE', "Control Shape", "Update copy.shape_control"),
    ('CONTROL_PIVOT', "Pivot", "Update copy.shape_pivot"),
]

# CloudRig Lattice 形状参数枚举
CLOUDRIG_LATTICE_ITEMS = [
    ('NONE', "None", "Standard Bone Widget behavior"),
    ('LATTICE_ROOT', "Root", "Update lattice.shape_root"),
    ('LATTICE_SHAPE', "Lattice", "Update lattice.shape_lattice"),
]

# CloudRig Limb: Generic 形状参数枚举
CLOUDRIG_LIMB_GENERIC_ITEMS = [
    ('NONE', "None", "Standard Bone Widget behavior"),
    ('LIMB_STRETCH', "Stretch Shape", "Update chain.shape_stretch"),
    ('LIMB_STRETCH_ENDS', "Stretch Ends", "Update chain.shape_stretch_ends"),
    ('LIMB_FK', "FK Shape", "Update fk_chain.shape_fk"),
    ('LIMB_FK_ROOT', "FK Root Shape", "Update fk_chain.shape_fk_root"),
    ('LIMB_IK_MASTER', "IK Master", "Update ik_chain.shape_ik_master"),
    ('LIMB_IK_FIRST', "First IK", "Update ik_chain.shape_ik_first"),
    ('LIMB_IK_POLE', "IK Pole", "Update ik_chain.shape_pole"),
    ('LIMB_RUBBERHOSE', "Rubberhose", "Update limb.shape_rubberhose"),
]

# CloudRig Shoulder Bone 形状参数枚举
CLOUDRIG_SHOULDER_ITEMS = [
    ('NONE', "None", "Standard Bone Widget behavior"),
    ('SHOULDER_SHAPE', "Shoulder", "Update shoulder.shape_shoulder"),
]

# CloudRig Curve: With Hooks 形状参数枚举
CLOUDRIG_CURVE_HOOKS_ITEMS = [
    ('NONE', "None", "Standard Bone Widget behavior"),
    ('CURVE_ROOT', "Root", "Update curve.shape_root"),
    ('CURVE_POINT', "Point", "Update curve.shape_point"),
    ('CURVE_HANDLE', "Handle", "Update curve.shape_handle"),
    ('CURVE_BEZIER_CENTER', "Bezier Center", "Update curve.shape_bezier_center"),
    ('CURVE_BEZIER', "Bezier", "Update curve.shape_bezier"),
    ('CURVE_SPLINE_ROOT', "Spline Root", "Update curve.shape_spline_root"),
    ('CURVE_RADIUS', "Radius", "Update curve.shape_radius"),
]

# CloudRig 组件类型枚举（用于显示）
CLOUDRIG_COMPONENT_TYPE_ITEMS = [
    ('NONE', "None", "No CloudRig component"),
    ('Spine: Cartoon', "Spine: Cartoon", "Spine Cartoon component"),
    ('Spine: IK/FK', "Spine: IK/FK", "Spine IK/FK component"),
    ('Limb: Biped Leg', "Limb: Biped Leg", "Limb Biped Leg component"),
    ('Limb: Generic', "Limb: Generic", "Limb Generic component"),
    ('Chain: FK', "Chain: FK", "Chain FK component"),
    ('Chain: IK', "Chain: IK", "Chain IK component"),
    ('Chain: Toon', "Chain: Toon", "Chain Toon component"),
    ('Aim', "Aim", "Aim component"),
    ('Single Control', "Single Control", "Single Control component"),
    ('Shoulder Bone', "Shoulder Bone", "Shoulder Bone component"),
    ('Lattice', "Lattice", "Lattice component"),
    ('Curve: With Hooks', "Curve: With Hooks", "Curve With Hooks component"),
]


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

    # CloudRig 组件类型（自动检测）
    cloudrig_component_type: EnumProperty(
        name="Component",
        description="Detected CloudRig component type",
        items=CLOUDRIG_COMPONENT_TYPE_ITEMS,
        default='NONE',
    )

    # CloudRig Spine: Cartoon 集成
    cloudrig_spine_toon_param: EnumProperty(
        name="Shape",
        description="Select CloudRig Spine: Cartoon shape parameter to update",
        items=CLOUDRIG_SPINE_TOON_ITEMS,
        default='NONE',
    )

    # CloudRig Limb: Biped Leg 集成
    cloudrig_limb_leg_param: EnumProperty(
        name="Shape",
        description="Select CloudRig Limb: Biped Leg shape parameter to update",
        items=CLOUDRIG_LIMB_LEG_ITEMS,
        default='NONE',
    )

    # CloudRig Spine: IK/FK 集成
    cloudrig_spine_ikfk_param: EnumProperty(
        name="Shape",
        description="Select CloudRig Spine: IK/FK shape parameter to update",
        items=CLOUDRIG_SPINE_IKFK_ITEMS,
        default='NONE',
    )

    # CloudRig Chain: FK 集成
    cloudrig_chain_fk_param: EnumProperty(
        name="Shape",
        description="Select CloudRig Chain: FK shape parameter to update",
        items=CLOUDRIG_CHAIN_FK_ITEMS,
        default='NONE',
    )

    # CloudRig Chain: IK 集成
    cloudrig_chain_ik_param: EnumProperty(
        name="Shape",
        description="Select CloudRig Chain: IK shape parameter to update",
        items=CLOUDRIG_CHAIN_IK_ITEMS,
        default='NONE',
    )

    # CloudRig Chain: Toon 集成
    cloudrig_chain_toon_param: EnumProperty(
        name="Shape",
        description="Select CloudRig Chain: Toon shape parameter to update",
        items=CLOUDRIG_CHAIN_TOON_ITEMS,
        default='NONE',
    )

    # CloudRig Aim 集成
    cloudrig_aim_param: EnumProperty(
        name="Shape",
        description="Select CloudRig Aim shape parameter to update",
        items=CLOUDRIG_AIM_ITEMS,
        default='NONE',
    )

    # CloudRig Single Control 集成
    cloudrig_single_control_param: EnumProperty(
        name="Shape",
        description="Select CloudRig Single Control shape parameter to update",
        items=CLOUDRIG_SINGLE_CONTROL_ITEMS,
        default='NONE',
    )

    # CloudRig Lattice 集成
    cloudrig_lattice_param: EnumProperty(
        name="Shape",
        description="Select CloudRig Lattice shape parameter to update",
        items=CLOUDRIG_LATTICE_ITEMS,
        default='NONE',
    )

    # CloudRig Limb: Generic 集成
    cloudrig_limb_generic_param: EnumProperty(
        name="Shape",
        description="Select CloudRig Limb: Generic shape parameter to update",
        items=CLOUDRIG_LIMB_GENERIC_ITEMS,
        default='NONE',
    )

    # CloudRig Shoulder Bone 集成
    cloudrig_shoulder_param: EnumProperty(
        name="Shape",
        description="Select CloudRig Shoulder Bone shape parameter to update",
        items=CLOUDRIG_SHOULDER_ITEMS,
        default='NONE',
    )

    # CloudRig Curve: With Hooks 集成
    cloudrig_curve_hooks_param: EnumProperty(
        name="Shape",
        description="Select CloudRig Curve: With Hooks shape parameter to update",
        items=CLOUDRIG_CURVE_HOOKS_ITEMS,
        default='NONE',
    )

    # Nested Property Groups
    custom_edit_color_set: PointerProperty(type=CustomColorSet)
    custom_pose_color_set: PointerProperty(type=CustomColorSet)


save_timer = None


def debounce_save(context):
    """Schedule saving the color sets 1 second after the last change."""
    from .functions.json_functions import save_color_sets
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
        if not context.window_manager.turn_off_colorset_save and not context.scene.bw_settings.lock_colorset_color_changes:
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
