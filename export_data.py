from stat import filemode
import bpy
import bpy_extras.io_utils
import json
import os

os.system("cls")

# ===========================================================


def pascal_voc_to_yolo(x_min, y_min, x_max, y_max, image_w, image_h):
    return [
        ((x_max + x_min) / 2) / image_w,
        ((y_max + y_min) / 2) / image_h,
        (x_max - x_min) / image_w,
        (y_max - y_min) / image_h,
    ]


def write_txt(path, content):
    with open(path, "a") as f:
        content += "\n"
        f.write(content)
        f.close()


def create_folder(path, folder_name):
    new_folder_path = f"{path}{folder_name}"
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
        # print(f"created new folder {new_folder_path} ")
    else:
        print(f"folder {folder_name} already exists")
    return new_folder_path


# ===========================================================


def export(
    self,
    arm,
    frame_start,
    frame_end,
    txt_path,
    class_id,
    YOLO,
    COCO,
    PASCAL_VOC,
):

    try:
        cam = bpy.data.objects["Camera"]

        # ===========================================================
        # create folders for export types

        YOLO_folder_path, COCO_folder_path, PASCAL_VOC_folder_path = None, None, None

        if YOLO == True:
            YOLO_folder_path = create_folder(txt_path, "YOLO")
        if COCO == True:
            COCO_folder_path = create_folder(txt_path, "COCO")
        if PASCAL_VOC == True:
            PASCAL_VOC_folder_path = create_folder(txt_path, "PASCAL_VOC")

        # ===========================================================

        bones_info = {}
        # bones_info : [
        # 		# [frame, head, tail]
        # 		[1, head, tail],
        #  		... ]

        for bone in arm.pose.bones:
            bones_info[bone.name] = []

        # ===========================================================

        scene = bpy.context.scene
        render_scale = scene.render.resolution_percentage / 100
        render_size = (
            int(scene.render.resolution_x * render_scale),
            int(scene.render.resolution_y * render_scale),
        )

        yolo_co = {}
        for frame in range(frame_start, frame_end + 1):
            bpy.context.scene.frame_set(frame)

            bones_coords = {
                "top_left": (),
                "top_right": (),
                "bottom_left": (),
                "bottom_right": (),
            }

            for bone in arm.pose.bones:
                arm_matrix = arm.matrix_world
                bone_world_head = arm_matrix @ bone.head

                co_2d = bpy_extras.object_utils.world_to_camera_view(
                    scene, cam, bone_world_head
                )

                co_2d_x = round(co_2d.x * render_size[0])
                co_2d_y = render_size[1] - round(co_2d.y * render_size[1])

                bones_coords[bone.name] = (co_2d_x, co_2d_y)
                # bones_info[bone.name] += [[frame, co_2d_x, co_2d_y]]

            # # pascal_voc
            # print(
            #     "\n pascal_voc\n" f"x_min:{bones_coords['top_left'][0]}",
            #     f"y_min:{bones_coords['top_left'][1]}",
            #     f"x_max:{bones_coords['bottom_right'][0]}",
            #     f"y_max:{bones_coords['bottom_right'][1]}",
            # )

            # coco
            width = bones_coords["top_right"][0] - bones_coords["top_left"][0]
            height = bones_coords["bottom_left"][1] - bones_coords["top_left"][1]
            # print(
            #     "\n coco\n" f"x_min:{bones_coords['top_left'][0]}",
            #     f"y_min:{bones_coords['top_left'][1]}",
            #     f"width:{width}",
            #     f"height:{height}",
            # )

            # yolo
            yolo_coords = pascal_voc_to_yolo(
                bones_coords["top_left"][0],
                bones_coords["top_left"][1],
                bones_coords["bottom_right"][0],
                bones_coords["bottom_right"][1],
                scene.render.resolution_x,
                scene.render.resolution_y,
            )
            # print(
            #     "\n yolo\n" f"x_center: {yolo_coords[0]}",
            #     f"y_center: {yolo_coords[1]}",
            #     f"width: {yolo_coords[2]}",
            #     f"height: {yolo_coords[3]}",
            # )

            yolo_co[frame] = [
                yolo_coords[0],
                yolo_coords[1],
                yolo_coords[2],
                yolo_coords[3],
            ]

            # ===========================================================
            # exporting data to txt files

            file_name_YOLO = f"{YOLO_folder_path}/{frame:006}.txt"
            file_name_COCO = f"{COCO_folder_path}/{frame:006}.txt"
            file_name_PASCAL_VOC = f"{PASCAL_VOC_folder_path}/{frame:006}.txt"

            # print(f"YOLO_folder_path {YOLO_folder_path} ")
            # print(f"file_name_YOLO   {file_name_YOLO} ")
            # # print(f"COCO_folder_path {COCO_folder_path} ")
            # # print(f"file_name_COCO   {file_name_COCO} ")
            # print(f"PASCAL_VOC_folder_path {PASCAL_VOC_folder_path} ")
            # # print(f"file_name_PASCAL_VOC   {file_name_PASCAL_VOC} ")

            if YOLO == True:
                content = f"{class_id} {yolo_coords[0]} {yolo_coords[1]} {yolo_coords[2]} {yolo_coords[3]}"
                write_txt(file_name_YOLO, content)
            if COCO == True:
                content = f"{class_id} {width} {height}"
                write_txt(file_name_COCO, content)
            if PASCAL_VOC == True:
                content = f"{class_id} {bones_coords['top_left'][1]},{bones_coords['bottom_right'][0]},{bones_coords['bottom_right'][1]}"
                write_txt(file_name_PASCAL_VOC, content)

        # # ===========================================================

        # # YOLO format is : object-class x y width height

        # # Serializing json
        # json_object = json.dumps(yolo_co, indent=4)

        # # Writing to sample.json
        # with open("C:\\Users\\Dime\\Desktop\\txt\\sample.json", "w") as outfile:
        #     outfile.write(json_object)

    except:
        self.report({"ERROR"}, f"No camera in 3D scene")
