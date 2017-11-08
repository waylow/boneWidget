'''
Copyright (C) 2016 Manuel Rais
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
    "author": "Manuel Rais, Christophe Seux",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Rigging"}
'''
if "bpy" in locals():
    import imp
    imp.reload(operators)
    imp.reload(panels)
'''

from . import operators
from . import panels
from .functions import readWidgets
    
import bpy
import os




def register():
    
    bpy.utils.register_module(__name__)
    

    
def unregister():
    bpy.utils.unregister_module(__name__)


    
'''
if __name__ == "__main__":
    register()
    
'''