# blender rounds fps even if is available in drop down menu

import bpy
from math import radians
import os

os.system("cls")

# ===============================================================


def create_collection(coll_name):
    collection = bpy.data.collections.new(coll_name)
    bpy.context.scene.collection.children.link(collection)


# ===============================================================

# main script
def camera_set_up(filepath):

    # create collection
    cam_coll_name = "Camera"
    if cam_coll_name not in bpy.data.collections:
        create_collection(cam_coll_name)
    # rename collection if it already exists
    else:
        print(f"[-] collection named {cam_coll_name} already exists")
        for i in range(1, 40):
            i = f"{i:003}"
            new_cam_coll_name = f"{cam_coll_name}_{i}"
            if (new_cam_coll_name in bpy.data.collections) == False:
                cam_coll_name = new_cam_coll_name
                create_collection(cam_coll_name)
                break

    # ===============================================================

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
    for coll in my_cam.users_collection:
        coll.objects.unlink(my_cam)
    coll_target = bpy.context.scene.collection.children.get(cam_coll_name)
    coll_target.objects.link(my_cam)

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
        23.98,
        24,
        25,
        29.97,
        30,
        50,
        59.94,
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
