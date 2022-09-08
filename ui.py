import bpy
import os
from bpy_extras.io_utils import ImportHelper, ExportHelper

from bpy.types import Operator, Panel
from bpy.props import (
    StringProperty,
    FloatVectorProperty,
    IntProperty,
    BoolProperty,
)

# from bpy.props import StringProperty

from . import import_video, bounding_box, export_data, collection_functional

CLASS_ID = None

PROPS = [
    (
        "YOLO",
        BoolProperty(name="YOLO", default=True),
    ),
    (
        "COCO",
        BoolProperty(name="COCO", default=False),
    ),
    (
        "PASCAL_VOC",
        BoolProperty(name="PASCAL_VOC", default=False),
    ),
    (
        "bounding_box",
        StringProperty(
            name="box name",
            default="bb",
        ),
    ),
    (
        "box_color",
        FloatVectorProperty(
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
        StringProperty(
            name="class",
            default="class name",
        ),
    ),
    (
        "class_id",
        IntProperty(
            name="Class ID",
            default=0,
            min=0,
        ),
    ),
    (
        "path",
        StringProperty(
            name="Export",
            description="Path to Directory",
            default="",
            # default="None",
            maxlen=1024,
            subtype="DIR_PATH",
        ),
    ),
]

# ===========================================================


class ImportVideoOperator(Operator, ImportHelper):
    bl_idname = "opr.import_video"
    bl_label = "Import Video"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        import_video.camera_set_up(self.filepath)
        return {"FINISHED"}


# ===========================================================


class AddBoundingBoxOperator(Operator):
    bl_idname = "opr.bounding_box_operator"
    bl_label = "bound box"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bounding_box.bounding_box_set_up(
            self,
            context.scene.bounding_box,
            # context.scene.class_id,
            context.scene.box_color,
        )
        return {"FINISHED"}


# ===========================================================


class ExportData(Operator):
    bl_idname = "opr.export_operator"
    bl_label = "export data"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        YOLO = context.scene.YOLO
        COCO = context.scene.COCO
        PASCAL_VOC = context.scene.PASCAL_VOC

        export_path = bpy.path.abspath(context.scene.path)
        # print(f"context.scene.path      {context.scene.path} ")
        # print(f"bpy.path.abspath        {bpy.path.abspath(context.scene.path)} ")
        # print(f"export_path             {export_path} ")

        if os.path.isdir(export_path) == True:
            good_bb = {}
            good_col = []

            # getting colletion with custom props
            for col in bpy.data.collections:
                prop = col.get("class_id")

                # getting colletion if it has custom prop and object(s)
                if prop != None and len(col.all_objects) != 0:
                    good_col.append(col.name)  # for pop up mesages
                    for o in col.all_objects:
                        # getting armature with correct bone names
                        if o.type == "ARMATURE":
                            if (
                                ("root" in o.pose.bones)
                                and ("top_left" in o.pose.bones)
                                and ("bottom_right" in o.pose.bones)
                                and ("top_right" in o.pose.bones)
                                and ("bottom_left" in o.pose.bones)
                            ):
                                good_bb[o] = prop
                            else:
                                print(f"[-] {o.name} has different bone names")

            if len(good_col) == 0:
                self.report(
                    {"ERROR"},
                    f"No collections with id found, or no armature in that collection",
                )
                del good_col

            # ===========================================================

            frame_start = bpy.context.scene.frame_start
            frame_end = bpy.context.scene.frame_end
            for obj, id in good_bb.items():
                export_data.export(
                    self,
                    obj,
                    frame_start,
                    frame_end,
                    export_path,
                    id,
                    YOLO,
                    COCO,
                    PASCAL_VOC,
                )
        else:
            self.report({"ERROR"}, f"Path selected {export_path} isn't a folder")
        return {"FINISHED"}


# ===========================================================


class ADD_CLASS(Operator):
    bl_idname = "wm.textop"
    bl_label = "Class name and ID"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        collection_functional.create_blue_collection(
            context.scene.class_name, context.scene.class_id
        )
        return {"FINISHED"}


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


class UiPanel(Panel):
    bl_idname = "VIEW3D_PT_ui"
    bl_label = "Blender Labelling Tool"
    bl_category = "Blender Labelling Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        # # ===========================================================

        box = layout.box()
        box.label(text="Import Video")
        box.operator("opr.import_video", text="Import Video")

        # # ===========================================================

        box = layout.box()
        box.label(text="Bounding Box")
        box.prop(context.scene, "bounding_box")
        box.prop(context.scene, "box_color")
        box.operator("opr.bounding_box_operator", text="Add Bounding Box")
        box.separator()

        # # ===========================================================

        box = layout.box()
        box.label(text="Class IDs")
        box.prop(context.scene, "class_name")
        box.prop(context.scene, "class_id")
        box.operator("wm.textop", text="Add New Class ID")
        box.separator()

        # # ===========================================================

        # self.layout.prop_search(bpy.context.scene,"target",bpy.context.scene,"objects",text="Select Bounding Box")
        box = layout.box()
        box.label(text="Export Data")
        box.prop(context.scene, "path")
        box.operator("opr.export_operator", text="Export data")

        col = layout.column()
        col_yolo = layout.column()
        col_coco = layout.column()
        col_pascal = layout.column()

        col_yolo.prop(context.scene, "YOLO")
        col_coco.prop(context.scene, "COCO")
        col_pascal.prop(context.scene, "PASCAL_VOC")

        col_coco.enabled = False
        col_pascal.enabled = False

        # row = self.layout.row()
        # box = layout.box()
        # box.label(text="testing unchecked")

        # box.enabled = True
        # box.prop(context.scene, "YOLO")
        # box.prop(context.scene, "COCO")
        # context.scene.COCO = False
