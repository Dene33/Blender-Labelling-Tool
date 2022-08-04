import bpy
import os
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

# from bpy.props import StringProperty

from . import import_video, bounding_box, export_data

PROPS = [
    (
        "bounding_box",
        bpy.props.StringProperty(name="bounding_box", default="bb"),
    ),
    (
        "bounding_box_obj",
        bpy.props.StringProperty(name="bounding_box_obj", default="bbo"),
    ),
    (
        "class_id",
        bpy.props.StringProperty(name="class_id", default="class id"),
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
            context.scene.class_id,
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
            target_obj = context.scene.target

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
class MATERIAL_UL_matslots_example(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        ob = data
        slot = item
        ma = slot.material
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            # You should always start your row layout by a label (icon + text), or a non-embossed text field,
            # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
            # We use icon_value of label, as our given icon is an integer value, not an enum ID.
            # Note "data" names should never be translated!
            if ma:
                layout.prop(ma, "name", text="", emboss=False, icon_value=icon)
            else:
                layout.label(text="", translate=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {"GRID"}:
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


# ===========================================================


class WM_textOp(Operator):
    bl_idname = "wm.textop"
    bl_label = "text tool"
    bl_options = {"REGISTER", "UNDO"}

    # text = bpy.props.StringParameter(name="enter class")
    class_name: bpy.props.StringProperty(name="Class Name", default="")
    class_id: bpy.props.IntProperty(name="Class ID", default=1)

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# ===========================================================

bpy.types.Scene.target = bpy.props.PointerProperty(type=bpy.types.Object)


class UiPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_ui"
    bl_label = "Blender Labelling Tool"
    bl_category = "Blender Labelling Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):

        col = self.layout.column()
        row = col.row()
        layout = self.layout

        col.operator("opr.import_video", text="Import Video")

        box = layout.box()
        # row = box.row()
        box.label(text="Bounding Box")
        box.prop(context.scene, "bounding_box")
        box.prop(context.scene, "bounding_box_obj")
        box.prop(context.scene, "my_color")
        box.operator("opr.bounding_box_operator", text="Add Bounding Box")
        # col = box.row()

        # for (prop_name, _) in PROPS:
        #     row = col.row()
        #     print(prop_name)
        #     row.prop(context.scene, prop_name)

        # layout.prop(bpy.data.objects, "objects")

        box = layout.box()
        # row = box.row()
        box.label(text="Export Data")

        # self.layout.prop_search(
        #     bpy.context.scene,
        #     "target",
        #     bpy.context.scene,
        #     "objects",
        #     text="Select Bounding Box",
        # )

        box.operator("opr.export_operator", text="Export data")
        box.operator("wm.textop", text="Class name & id")

        # obj = context.object
        # layout.template_list(
        #     "MATERIAL_UL_matslots_example",
        #     "compact",
        #     obj,
        #     "material_slots",
        #     obj,
        #     "active_material_index",
        #     type="COMPACT",
        # )
