'''
Copyright (C) 2020 Manuel Rais
manu@g-lul.com

Created by Manuel Rais and Christophe Seux

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Bone Widget",
    "author": "Manuel Rais, Christophe Seux, Bassam Kurdali, Wayne Dixon, Blender Defender, Max Nadolny, Adhi Hargo",
    "version": (1, 8),
    "blender": (2, 93, 0),
    "location": "UI > Properties Panel",
    "description": "Easily Create Bone Widgets",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Rigging"}

if "bpy" in locals():
    import importlib

    bl_class_registry.BlClassRegistry.cleanup()
    importlib.reload(keymaps)
    importlib.reload(operators)
    importlib.reload(prefs)
    importlib.reload(panels)
    importlib.reload(menus)
    importlib.reload(functions)
else:
    import bpy
    from . import bl_class_registry
    from . import keymaps
    from . import operators
    from . import prefs
    from . import panels
    from . import menus
    from . import functions

import bpy


def check_version(major, minor, _):
    """
    Check blender version
    """

    if bpy.app.version[0] == major and bpy.app.version[1] == minor:
        return 0
    if bpy.app.version[0] > major:
        return 1
    if bpy.app.version[1] > minor:
        return 1
    return -1


classes = [
    panels.BONEWIDGET_PT_posemode_panel,
    menus.BONEWIDGET_MT_bw_specials,
    menus.BONEWIDGET_MT_pie,
    prefs.BoneWidgetPreferences,
]


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    operators.register()
    bl_class_registry.BlClassRegistry.register()
    keymaps.register()

    # Apply preferences of the panel location.
    context = bpy.context
    preferences = functions.getPreferences(context)
    # Only default panel location is available in < 2.80
    if check_version(2, 80, 0) < 0:
        preferences.panel_category = "Rig Tools"
    prefs.BoneWidgetPreferences.panel_category_update_fn(preferences, context)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    keymaps.unregister()
    # TODO: Unregister by BlClassRegistry
    bl_class_registry.BlClassRegistry.unregister()
    operators.unregister()


if __name__ == "__main__":
    register()
