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

if "bpy" in locals():
    import importlib
    importlib.reload(prefs)
    importlib.reload(panels)
    importlib.reload(menus)

else:
    import bpy
    from . import operators
    from . import panels
    from . import prefs
    from . import menus

import bpy


def get_user_preferences(context):
    if hasattr(context, "user_preferences"):
        return context.user_preferences

    return context.preferences


def register():
    operators.register()
    menus.register()
    prefs.register()

    # Apply preferences of the panel location.
    context = bpy.context
    pref = get_user_preferences(context).addons[__package__].preferences
    prefs.BoneWidget_preferences.panel_category_update_fn(pref, context)
    panels.register()

def unregister():
    operators.unregister()
    menus.unregister()
    prefs.unregister()

    panels.unregister()
