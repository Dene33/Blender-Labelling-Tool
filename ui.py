import bpy
import os
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

# from bpy.props import StringProperty

from . import import_video, bounding_box, export_data

PROPS = [
    (
        "bounding_box",
        bpy.props.StringProperty(name="box name", default="bb"),
    ),
    # (
    #     "bounding_box_obj",
    #     bpy.props.StringProperty(name="bounding_box_obj", default="bbo"),
    # ),
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
class MATERIAL_UL_matslots_example(bpy.types.UIList):
    # The draw_item function is called for each item of the collection that is visible in the list.
    #   data is the RNA object containing the collection,
    #   item is the current drawn item of the collection,
    #   icon is the "computed" icon for the item (as an integer, because some objects like materials or textures
    #   have custom icons ID, which are not available as enum items).
    #   active_data is the RNA object containing the active property for the collection (i.e. integer pointing to the
    #   active item of the collection).
    #   active_propname is the name of the active property (use 'getattr(active_data, active_propname)').
    #   index is index of the current item in the collection.
    #   flt_flag is the result of the filtering process for this item.
    #   Note: as index and flt_flag are optional arguments, you do not have to use/declare them here if you don't
    #         need them.
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
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


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


class AddEntry(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        print(
            f"self {self} \n context {context} \n layout {layout} \n data {data} \n item {item} \n icon {icon} \n active_data {active_data} \n active_propname {active_propname} \n "
        )

        scene = data
        ob = item
        # print(data, item, active_data, active_propname)

        if self.layout_type in {"DEFAULT", "COMPACT"}:

            layout.prop(ob, "name", text="", emboss=False, icon_value=layout.icon(ob))


# ===========================================================

# bpy.types.Scene.target = bpy.props.PointerProperty(type=bpy.types.Object)


class UiPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_ui"
    bl_label = "Blender Labelling Tool"
    bl_category = "Blender Labelling Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):

        col = self.layout.column()
        # row = col.row()
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

        # ===========================================================

        obj = context.object
        layout.template_list(
            "MATERIAL_UL_matslots_example",
            "compact",
            obj,
            "material_slots",
            obj,
            "active_material_index",
            type="COMPACT",
        )

        # obj = context.object
        # scn = context.scene
        # layout = self.layout
        # # col = layout.column()
        # col.template_list(
        #     "AddEntry",
        #     "",
        #     obj,
        #     "objects",
        #     obj,
        #     "active_object_index",
        # )
