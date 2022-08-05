import bpy

from bpy.types import PropertyGroup

from bpy.props import (
    CollectionProperty,
    IntProperty,
    BoolProperty,
    StringProperty,
    PointerProperty,
)


class MATERIAL_UL_extreme_matslot(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        scene = data
        ob = item
        #print(data, item, active_data, active_propname)
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            layout.prop(ob, "name", text="", emboss=False, icon_value=layout.icon(ob))


class SCENE_PT_materials(bpy.types.Panel):

    bl_label = "My label"
    bl_idname = "SCENE_PT_materials"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "My Category"

    def draw(self, context):

        scn = context.scene
        layout = self.layout
        col = layout.column()
        col.template_list(
            "MATERIAL_UL_extreme_matslot",
            "",
            scn,
            "objects",
            scn,
            "active_object_index")







classes = (
           MATERIAL_UL_extreme_matslot,
           SCENE_PT_materials)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.active_object_index = IntProperty()


def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)


if __name__ == "__main__":
    register()