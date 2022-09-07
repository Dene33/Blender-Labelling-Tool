# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Blender Labelling Tool",
    "author": "demania",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 11),
    "location": "",
    "warning": "",
    "category": "Generic",
}

# ===========================================================


import bpy


from .ui import (
    ImportVideoOperator,
    UiPanel,
    AddBoundingBoxOperator,
    ExportData,
    ADD_CLASS,
    GU_PT_collection_custom_properties,
)

# ===========================================================


classes = [
    ImportVideoOperator,
    UiPanel,
    AddBoundingBoxOperator,
    ExportData,
    ADD_CLASS,
    GU_PT_collection_custom_properties,
]
# ===========================================================


def register():
    for (prop_name, prop_value) in ui.PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for (prop_name, _) in ui.PROPS:
        delattr(bpy.types.Scene, prop_name)

    for c in classes:
        bpy.utils.unregister_class(c)
