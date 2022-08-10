import bpy
import os
from bpy_extras.io_utils import ImportHelper

from bpy.types import Operator, Panel, PropertyGroup, UIList

# from bpy.props import StringProperty

from . import import_video, bounding_box, export_data

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
            default=(1.0, 1.0, 1.0, 1.0),
            size=4,
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
        """Do something with the selected file(s)."""

        filename, extension = os.path.splitext(self.filepath)

        # print("File name:", filename)
        # print("File extension:", extension)

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

        file_path = self.filepath
        # check if inputted path is folder
        if os.path.isdir(file_path) == True:
            print("File name:", file_path)

            # get amrature obj selected by user
            # target_obj = context.scene.target
            target_obj = bpy.context.active_object

            if target_obj == None:
                self.report({"ERROR"}, f"No object selected")
            else:
                t_name = target_obj.name
                if target_obj.type != "ARMATURE":
                    self.report({"ERROR"}, f"Object '{t_name}' isn't armature")
                else:
                    frame_start = bpy.context.scene.frame_start
                    frame_end = bpy.context.scene.frame_end
                    print(t_name, frame_start, frame_end)
                    export_data.export(
                        target_obj.name,
                        frame_start,
                        frame_end,
                        file_path,
                    )
        else:
            self.report({"ERROR"}, f"Path selected isn't a folder")
        return {"FINISHED"}


# ===========================================================


class WM_textOp(Operator):
    bl_idname = "wm.textop"
    bl_label = "Class name and ID"
    bl_options = {"REGISTER", "UNDO"}

    # text = bpy.props.StringParameter(name="enter class")
    class_name: bpy.props.StringProperty(name="Class Name", default="")
    class_id: bpy.props.IntProperty(name="Class ID", default=1)

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# ===========================================================


class CUSTOM_OT_actions(Operator):
    """Move items up and down, add and remove"""

    bl_idname = "custom.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {"REGISTER"}

    class_name: bpy.props.StringProperty(name="class", default="class")
    id: bpy.props.IntProperty(name="id", default=0, min=0)

    action: bpy.props.EnumProperty(
        items=(
            # ("UP", "Up", ""),
            # ("DOWN", "Down", ""),
            ("REMOVE", "Remove", ""),
            ("ADD", "Add", ""),
        )
    )

    # def random_color(self):
    #     from mathutils import Color
    #     from random import random
    #     return Color((random(), random(), random()))

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.custom_index

        print(f"idx {idx} ")
        print(f"custom_index {scn.custom_index} ")
        print(f"scn.custom {scn.custom} {type(scn.custom)} ")
        try:
            item = scn.custom[idx]
        except IndexError:
            pass
        else:
            # if self.action == "DOWN" and idx < len(scn.custom) - 1:
            #     item_next = scn.custom[idx + 1].name
            #     scn.custom.move(idx, idx + 1)
            #     scn.custom_index += 1
            #     info = 'Item "%s" moved to position %d' % (
            #         item.name,
            #         scn.custom_index + 1,
            #     )
            #     self.report({"INFO"}, info)

            # elif self.action == "UP" and idx >= 1:
            #     item_prev = scn.custom[idx - 1].name
            #     scn.custom.move(idx, idx - 1)
            #     scn.custom_index -= 1
            #     info = 'Item "%s" moved to position %d' % (
            #         item.name,
            #         scn.custom_index + 1,
            #     )
            #     self.report({"INFO"}, info)

            if self.action == "REMOVE":
                item = scn.custom[scn.custom_index]
                mat = item.material
                if mat:
                    mat_obj = bpy.data.materials.get(mat.name, None)
                    if mat_obj:
                        bpy.data.materials.remove(mat_obj, do_unlink=True)
                info = f"Item {item} removed from scene"
                scn.custom.remove(idx)
                if scn.custom_index == 0:
                    scn.custom_index = 0
                else:
                    scn.custom_index -= 1
                self.report({"INFO"}, info)

        if self.action == "ADD":
            item = scn.custom.add()
            item.id = len(scn.custom)
            print(f"item {item} ")
            item.material = bpy.data.materials.new(name=context.scene.class_name)
            item.name = item.material.name
            # col = self.random_color()
            # item.material.diffuse_color = (col.r, col.g, col.b, 1.0)
            scn.custom_index = len(scn.custom) - 1
            info = "%s added to list" % (item.name)
            self.report({"INFO"}, info)
        return {"FINISHED"}


# ===========================================================


class CUSTOM_UL_items(UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        mat = item.material
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            split = layout.split(factor=0.3)
            # split.label(text=f"Index: {context.scene.id}")
            split.label(text=f"Index: {index}")
            # static method UILayout.icon returns the integer value of the icon ID
            # "computed" for the given RNA object.
            split.prop(mat, "name", text="", emboss=True)
            split.prop(mat, "name", text="txt", emboss=True)

        elif self.layout_type in {"GRID"}:
            layout.alignment = "LEFT"
            layout.label(text="", icon_value=layout.icon(mat))

    def invoke(self, context, event):
        pass


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

        col.operator("opr.import_video", text="Import Video")

        box = layout.box()
        # row = box.row()
        box.label(text="Bounding Box")
        box.prop(context.scene, "bounding_box")
        box.prop(context.scene, "my_color")
        box.operator("opr.bounding_box_operator", text="Add Bounding Box")
        # col = box.row()

        # for (prop_name, _) in PROPS:
        #     row = col.row()
        #     row.prop(context.scene, prop_name)

        box = layout.box()
        box.label(text="Export Data")

        # self.layout.prop_search(bpy.context.scene,"target",bpy.context.scene,"objects",text="Select Bounding Box")

        box.operator("opr.export_operator", text="Export data")
        # box.operator("wm.textop", text="Class name & id")

        # # ===========================================================

        box = layout.box()
        box.label(text="Class id")

        rows = 2
        box.template_list(
            "CUSTOM_UL_items",
            "custom_def_list",
            scn,
            "custom",
            scn,
            "custom_index",
            rows=4,
        )
        box.separator()

        # class_props = self.layout.operator(CUSTOM_OT_actions.bl_idname)
        # class_props.class_name = box.prop(context.scene, "class_name")
        # class_props.id = box.prop(context.scene, "id")

        col.prop(context.scene, "class_name")
        col.prop(context.scene, "id")
        box.separator()

        box = box.column(align=True)
        box.operator(CUSTOM_OT_actions.bl_idname, icon="ADD", text="").action = "ADD"
        box.operator(
            CUSTOM_OT_actions.bl_idname, icon="REMOVE", text=""
        ).action = "REMOVE"
