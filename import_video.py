# blender rounds fps even if is available in drop down menu

import bpy
from math import radians
import os

from . import collection_functional


os.system("cls")

# ===============================================================


# main script
def camera_set_up(filepath):
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    # create collection
    cam_coll_name = "Camera"
    cam_coll_name = collection_functional.create_collection(cam_coll_name, True)

    # ===============================================================

    # delete exising camera
    bpy.ops.object.select_all(action="DESELECT")
    for o in bpy.data.objects:
        o.select_set(False)
        if o.type == "CAMERA":
            o.select_set(True)
            bpy.ops.object.delete()

    # create camera and displace it -10 m Y, 90 degrees on X
    bpy.ops.object.camera_add(
        location=(0, -10, 0),
        rotation=(radians(90), radians(0), radians(0)),
        scale=(1, 1, 1),
    )
    my_cam = bpy.context.active_object

    # set camera ORTHO and scale 6
    my_cam.data.type = "ORTHO"
    my_cam.data.ortho_scale = 6

    # ===============================================================

    # unlink camera from collection and link to Camera collection created
    collection_functional.link_to_collection(cam_coll_name, my_cam)

    # ===============================================================

    # load movie clip
    vid = bpy.data.movieclips.load(filepath)
    my_cam.data.show_background_images = True
    bg = my_cam.data.background_images.new()
    bg.source = "MOVIE_CLIP"
    bg.clip = vid

    # ===============================================================

    # set scene resolution
    bpy.context.scene.render.resolution_x = vid.size[0]
    bpy.context.scene.render.resolution_y = vid.size[1]

    bl_frame_rates = [
        # 23.98,
        24,
        25,
        # 29.97,
        30,
        50,
        # 59.94,
        60,
        120,
        240,
    ]

    diff = abs(vid.fps - bl_frame_rates[0])
    frame_rate = bl_frame_rates[0]
    for bl_fr in bl_frame_rates:
        if abs(bl_fr - vid.fps) < diff:
            frame_rate = bl_fr
            diff = abs(bl_fr - vid.fps)

    # set frame rate to closest frame_rate available in blender
    bpy.context.scene.render.fps = frame_rate
    # print(f"bpy.context.scene.render.fps = {frame_rate}")

    # ===============================================================


# camera_set_up(
#     "C:/Users/Dime/Downloads/mixkit-full-shot-of-a-group-of-friends-dancing-40356.mp4"
# )
