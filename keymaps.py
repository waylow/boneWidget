import bpy

from . import menus

addon_keymaps = []


def can_register():
    # true if Blender run with GUI
    return not bpy.app.background


def register():
    if not can_register():
        return

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new("Pose", space_type="EMPTY")
    kmi = km.keymap_items.new("wm.call_menu_pie", type="E", value="PRESS")
    kmi.properties.name = menus.BONEWIDGET_MT_pie.bl_idname

    addon_keymaps.append(km)


def unregister():
    if not can_register():
        return

    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
