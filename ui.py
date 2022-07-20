import bpy
import os
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty


from . import labeling_bones, bounding_box

# from . import bounding_box

PROPS = [
    (
        "bounding_box",
        bpy.props.StringProperty(name="bounding_box", default="bb"),
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
    # ("add_version", bpy.props.BoolProperty(name="Add Version", default=False)),
    # ("version", bpy.props.IntProperty(name="Version", default=1)),
]

# ===========================================================


class ImportVideoOperator(Operator, ImportHelper):
    bl_idname = "opr.import_video"
    bl_label = "Object Renamer"

    def execute(self, context):
        """Do something with the selected file(s)."""

        filename, extension = os.path.splitext(self.filepath)

        print("Selected file:", self.filepath)
        print("File name:", filename)
        print("File extension:", extension)
        # print("Some Boolean:", self.some_boolean)

        print("import vid")
        labeling_bones.camera_set_up(self.filepath)

        return {"FINISHED"}


# ===========================================================


class AddBoundingBoxOperator(Operator):

    bl_idname = "opr.bounding_box_operator"
    bl_label = "bound box"

    def execute(self, context):
        print("box")
        params = (
            context.scene.bounding_box,
            context.scene.my_color,
        )
        print(f"bounding_box    {context.scene.bounding_box}")
        print(f"my_color        {context.scene.my_color}")
        bounding_box.bounding_box_set_up(
            context.scene.bounding_box, context.scene.my_color
        )
        return {"FINISHED"}


# ===========================================================


class ImportVideoPanel(bpy.types.Panel):

    bl_idname = "VIEW3D_PT_import_video"
    bl_label = "Blender Labelling Tool"
    bl_category = "Blender Labelling Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        col = self.layout.column()
        col.operator("opr.import_video", text="Import Video")
        # col.operator("test.open_filebrowser", text="Import Video")
        for (prop_name, _) in PROPS:
            row = col.row()
            row.prop(context.scene, prop_name)

        col.operator("opr.bounding_box_operator", text="Add Bounding Box")
