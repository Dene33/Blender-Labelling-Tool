import bpy
import os
from bpy_extras.io_utils import ImportHelper

from bpy.types import Operator, Panel, PropertyGroup, UIList

# from bpy.props import StringProperty

from . import import_video, bounding_box, export_data, collection_functional

CLASS_ID = None

PROPS = [
    (
        "bounding_box",
        bpy.props.StringProperty(
            name="box name",
            default="bb",
        ),
    ),
    (
        "my_color",
        bpy.props.FloatVectorProperty(
            name="Bounding Box color",
            subtype="COLOR",
            size=4,
            min=0.0,
            max=1.0,
            default=(1.0, 1.0, 1.0, 1.0),
        ),
    ),
    (
        "class_name",
        bpy.props.StringProperty(
            name="class",
            default="class",
        ),
    ),
    (
        "id",
        bpy.props.IntProperty(
            name="id",
            default=0,
            min=0,
        ),
    ),
]

# ===========================================================


class ImportVideoOperator(Operator, ImportHelper):
    bl_idname = "opr.import_video"
    bl_label = "Import Video"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # filename, extension = os.path.splitext(self.filepath)
        import_video.camera_set_up(self.filepath)

        return {"FINISHED"}


# ===========================================================


class AddBoundingBoxOperator(Operator):
    bl_idname = "opr.bounding_box_operator"
    bl_label = "bound box"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bounding_box.bounding_box_set_up(
            context.scene.bounding_box,
            # context.scene.class_id,
            context.scene.my_color,
        )
        return {"FINISHED"}


# ===========================================================


class ExportData(Operator, ImportHelper):
    bl_idname = "opr.export_operator"
    bl_label = "export data"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        good_bb = {}

        print("\n\n\n==========================")
        # getting colletion with custom props
        for col in bpy.data.collections:
            prop = col.get("class_id")
            print(col.name)
            print(prop)
            print(len(col.all_objects))

            # getting colletion if it has custom prop and object(s)
            if prop != None and len(col.all_objects) != 0:
                print(f"\t{col}")

                for o in col.all_objects:
                    # getting armature with correct bone names
                    # bones = [o.names for o in o.pose.bones]
                    if o.type == "ARMATURE":
                        if (
                            ("root" in o.pose.bones)
                            and ("top_left" in o.pose.bones)
                            and ("bottom_right" in o.pose.bones)
                            and ("top_right" in o.pose.bones)
                            and ("bottom_left" in o.pose.bones)
                        ):
                            # print(f"[+] {o.name} has all bones")
                            good_bb[o] = prop
                            print(o)
                        else:
                            print(f"[-] {o.name} has different bone names")

        # # restructure dict to id : [object]
        # for k, v in good_bb.items():
        #     for k2, v2 in restructured_bb.items():
        #         if v == k2:
        #             restructured_bb[k2].append(k)

        # ===========================================================

        file_path = self.filepath
        # check if inputted path is folder
        print("File name:", file_path)
        if os.path.isdir(file_path) == True:
            frame_start = bpy.context.scene.frame_start
            frame_end = bpy.context.scene.frame_end
            for obj, id in good_bb.items():
                export_data.export(
                    self,
                    obj,
                    frame_start,
                    frame_end,
                    file_path,
                    id,
                )
        else:
            self.report({"ERROR"}, f"Path selected isn't a folder \n {file_path}")
        return {"FINISHED"}


# ===========================================================


class WM_textOp(Operator):
    bl_idname = "wm.textop"
    bl_label = "Class name and ID"
    bl_options = {"REGISTER", "UNDO"}

    class_name: bpy.props.StringProperty(name="Class Name", default="")
    class_id: bpy.props.IntProperty(name="Class ID", default=0, min=0)

    def execute(self, context):
        new_coll = collection_functional.create_collection(self.class_name, True)
        bpy.data.collections[new_coll].color_tag = "COLOR_05"

        # make colletion active
        collections = bpy.context.view_layer.layer_collection.children
        for collection in collections:
            if collection.name == new_coll:
                bpy.context.view_layer.active_layer_collection = collection
                bpy.data.collections[new_coll]["class_id"] = self.class_id
                global CLASS_ID
                CLASS_ID = self.class_id

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# ===========================================================

from rna_prop_ui import PropertyPanel

# custom panel to colletions
class GU_PT_collection_custom_properties(bpy.types.Panel, PropertyPanel):
    _context_path = "collection"
    _property_type = bpy.types.Collection
    bl_label = "Custom Properties"
    bl_idname = "GU_PT_collection_custom_properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "collection"


# ===========================================================

# class CUSTOM_OT_actions(Operator):
#     """Move items up and down, add and remove"""

#     bl_idname = "custom.list_action"
#     bl_label = "List Actions"
#     bl_description = "Move items up and down, add and remove"
#     bl_options = {"REGISTER"}

#     action: bpy.props.EnumProperty(
#         items=(
#             ("UP", "Up", ""),
#             ("DOWN", "Down", ""),
#             ("REMOVE", "Remove", ""),
#             ("ADD", "Add", ""),
#         )
#     )

#     def random_color(self):
#         from mathutils import Color
#         from random import random

#         return Color((random(), random(), random()))

#     def invoke(self, context, event):
#         scn = context.scene
#         idx = scn.custom_index

#         try:
#             item = scn.custom[idx]
#         except IndexError:
#             pass
#         else:
#             if self.action == "DOWN" and idx < len(scn.custom) - 1:
#                 item_next = scn.custom[idx + 1].name
#                 scn.custom.move(idx, idx + 1)
#                 scn.custom_index += 1
#                 info = f'Item "{item.name}" moved to position {scn.custom_index + 1}'
#                 self.report({"INFO"}, info)

#             elif self.action == "UP" and idx >= 1:
#                 item_prev = scn.custom[idx - 1].name
#                 scn.custom.move(idx, idx - 1)
#                 scn.custom_index -= 1
#                 info = f'Item "{item.name}" moved to position {scn.custom_index+1}'
#                 self.report({"INFO"}, info)

#             elif self.action == "REMOVE":
#                 item = scn.custom[scn.custom_index]
#                 mat = item.material
#                 if mat:
#                     mat_obj = bpy.data.materials.get(mat.name, None)
#                     if mat_obj:
#                         bpy.data.materials.remove(mat_obj, do_unlink=True)
#                 info = f"Item {item} removed from scene"
#                 scn.custom.remove(idx)
#                 if scn.custom_index == 0:
#                     scn.custom_index = 0
#                 else:
#                     scn.custom_index -= 1
#                 self.report({"INFO"}, info)

#         if self.action == "ADD":
#             item = scn.custom.add()
#             item.id = len(scn.custom)
#             item.material = bpy.data.materials.new(name="Material")
#             item.name = item.material.name
#             col = self.random_color()
#             item.material.diffuse_color = (col.r, col.g, col.b, 1.0)
#             scn.custom_index = len(scn.custom) - 1
#             info = f"{item.name} added to list"
#             self.report({"INFO"}, info)
#         return {"FINISHED"}

# class CUSTOM_UL_items(UIList):
#     def draw_item(
#         self, context, layout, data, item, icon, active_data, active_propname, index
#     ):
#         mat = item.material
#         if self.layout_type in {"DEFAULT", "COMPACT"}:
#             split = layout.split(factor=0.3)
#             split.label(text=f"Index: {index}")
#             # static method UILayout.icon returns the integer value of the icon ID
#             # "computed" for the given RNA object.
#             split.prop(mat, "name", text="", emboss=False, icon_value=layout.icon(mat))

#         elif self.layout_type in {"GRID"}:
#             layout.alignment = "CENTER"
#             layout.label(text="", icon_value=layout.icon(mat))

#     def invoke(self, context, event):
#         pass

# ===========================================================

# from bpy.props import PointerProperty

# class CUSTOM_PG_materialCollection(PropertyGroup):
#     # name: StringProperty() -> Instantiated by default
#     material: PointerProperty(name="Material", type=bpy.types.Material)

# class CUSTOM_PG_Collection(PropertyGroup):
#     class_name_prop: bpy.props.StringProperty(name="class", default="class")
#     id_prop: bpy.props.IntProperty(name="id", default=0, min=0)

# ===========================================================

# bpy.types.Scene.target = bpy.props.PointerProperty(type=bpy.types.Object)


class UiPanel(Panel):
    bl_idname = "VIEW3D_PT_ui"
    bl_label = "Blender Labelling Tool"
    bl_category = "Blender Labelling Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        col = self.layout.column()
        scn = bpy.context.scene
        layout = self.layout

        box = layout.box()
        box.label(text="Import Video")
        box.operator("opr.import_video", text="Import Video")

        # # ===========================================================

        box = layout.box()
        box.label(text="Bounding Box")
        box.prop(context.scene, "bounding_box")
        box.prop(context.scene, "my_color")
        box.operator("opr.bounding_box_operator", text="Add Bounding Box")
        box.separator()

        # # ===========================================================

        box = layout.box()
        box.label(text="Export Data")
        # self.layout.prop_search(bpy.context.scene,"target",bpy.context.scene,"objects",text="Select Bounding Box")
        box.operator("wm.textop", text="Add New Class ID")

        col = box.column(align=True)
        row = col.row(align=True)
        row.operator("opr.export_operator", text="Export data")
        # if context.selected_objects:
        #     row.operator("opr.export_operator", text="Export data")
        # else:
        #     row.enabled = False
        #     row.operator("opr.export_operator", text="select armature first")
        # box.separator()

        # # ===========================================================

        # box2 = layout.box()
        # box2.label(text="Class id")

        # box2.template_list("CUSTOM_UL_items","custom_def_list",scn,"custom",scn,"custom_index",rows=3)
        # box2.separator()

        # col = box2.column(align=True)
        # row = col.row(align=False)
        # row.prop(context.scene, "class_name")
        # row.prop(context.scene, "id")

        # box2.operator("custom.list_action", icon="ADD", text="").action = "ADD"
        # box2.operator("custom.list_action", icon="REMOVE", text="").action = "REMOVE"
