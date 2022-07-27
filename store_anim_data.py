import bpy
import bpy_extras.io_utils 
import os

os.system("cls")

def pascal_voc_to_yolo(x_min, y_min, x_max, y_max, image_w, image_h):
    return [((x_max + x_min) / 2) / image_w, ((y_max + y_min) / 2) / image_h, (x_max - x_min)/image_w, (y_max - y_min)/image_h]

# ===========================================================

frame_start = bpy.context.scene.frame_start
frame_end = bpy.context.scene.frame_end

# ===========================================================

arm = bpy.data.objects["bb"]

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
        
    bones_coords = {'top_left': (),
                     'top_right': (),
                     'bottom_left': (),
                     'bottom_right': ()}
    
    # print(frame)
    for bone in arm.pose.bones:
        arm_matrix = arm.matrix_world
        bone_world_head = arm_matrix @ bone.head
        
        co_2d = bpy_extras.object_utils.world_to_camera_view(scene, cam, bone_world_head)
        
        co_2d_x = (round(co_2d.x * render_size[0]))

        co_2d_y = (render_size[1]-round(co_2d.y * render_size[1]))
        
        bones_coords[bone.name] = (co_2d_x, co_2d_y)

        bones_info[bone.name] += [[frame, co_2d_x, co_2d_y]]
        # bones_info[bone.name] += [[frame, bone.head, bone.tail]]
    
    print('pascal_voc')
    print(f"x_min:{bones_coords['top_left'][0]}", f"y_min:{bones_coords['top_left'][1]}",
          f"x_max:{bones_coords['bottom_right'][0]}", f"y_max:{bones_coords['bottom_right'][1]}")
          
    print('coco')
    width = bones_coords['top_right'][0] - bones_coords['top_left'][0]
    height = bones_coords['bottom_left'][1] - bones_coords['top_left'][1]
    print(f"x_min:{bones_coords['top_left'][0]}", f"y_min:{bones_coords['top_left'][1]}",
          f"width:{width}", f"height:{height}")
          
    print('yolo')
    yolo_coords = pascal_voc_to_yolo(bones_coords['top_left'][0], bones_coords['top_left'][1],
                                     bones_coords['bottom_right'][0], bones_coords['bottom_right'][1],
                                     scene.render.resolution_x, scene.render.resolution_y)
    print(f"x_center: {yolo_coords[0]}", f"y_center: {yolo_coords[1]}", f"width: {yolo_coords[2]}", f"height: {yolo_coords[3]}")


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
