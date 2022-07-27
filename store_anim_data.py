import bpy
import bpy_extras.io_utils 
import os

os.system("cls")

# ===========================================================

frame_start = bpy.context.scene.frame_start
frame_end = bpy.context.scene.frame_end

# ===========================================================

arm = bpy.data.objects["dancer_00"]

# ===========================================================

bones_info = {}
# bones_info : [
# 		# [frame, head, tail]
# 		[1, head, tail],
# 		[2, head, tail],
#  		... ]

for bone in arm.pose.bones:
    bones_info[bone.name] = []

# ===========================================================

cam = bpy.data.objects["Camera"]
scene = bpy.context.scene
render_scale = scene.render.resolution_percentage / 100
render_size = (
    int(scene.render.resolution_x * render_scale),
    int(scene.render.resolution_y * render_scale),
)

for frame in range(frame_start, frame_end + 1):
    bpy.context.scene.frame_set(frame)

    # print(frame)
    for bone in arm.pose.bones:
        arm_matrix = arm.matrix_world
        bone_world_head = arm_matrix @ bone.head
        
        co_2d = bpy_extras.object_utils.world_to_camera_view(scene, cam, bone_world_head)
        
        co_2d_x = (round(co_2d.x * render_size[0]))
        co_2d_y = (round(co_2d.y * render_size[1]))
        
        co_2d_x2 = (round(co_2d.x * render_size[0]))
        co_2d_y2 = (render_size[1]-round(co_2d.y * render_size[1]))
        
        print(f" x  {co_2d_x}")
        print(f" x2 {co_2d_x2}")
        print(f" y  {co_2d_y}")
        print(f" y2 {co_2d_y2}")
        print()


        bones_info[bone.name] += [[frame, co_2d_x, co_2d_y]]
        # bones_info[bone.name] += [[frame, bone.head, bone.tail]]


# ===========================================================

# for k, v in bones_info.items():
#     print(k)
#     # print(v)
#     print(len(v))

print()
print("=====================")
print(bones_info["root"][0])
print(bones_info["root"][0][0])
print(bones_info["root"][0][1])
# print(bones_info["root"][20])
print("=====================")
