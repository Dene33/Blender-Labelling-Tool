import bpy
from math import radians
from . import import_video
import os

os.system("cls")

# ===========================================================


def make_bone(obj, b_name, b_parent=None, head=(0, 0, 0), tail=(0.5, 0, 0)):
    # obArm = bpy.context.active_object  # get the armature object
    ebs = obj.data.edit_bones
    newBone = ebs.new(b_name)
    newBone.head = head
    newBone.tail = tail
    if b_parent != None:
        newBone.parent = ebs[b_parent]


# ===========================================================


def get_constrain_name(bone, parent_obj):
    """get name of current constraint"""
    bone_constrtaint = parent_obj.pose.bones[bone]
    constraint_list = bone_constrtaint.constraints.keys()
    return constraint_list[len(constraint_list) - 1]


# ===========================================================


def bounding_box_set_up(name, color):
    # create collections
    arm_coll = import_video.create_collection(name)
    bone_shape_coll = import_video.create_collection("Bone Shapes", True)

    # ===========================================================
    # # create plane as custom obj for bone
    # bpy.ops.mesh.primitive_plane_add(size=2,enter_editmode=False,align="WORLD",location=(0, 0, 0),scale=(0.1, 0.1, 0.1),)

    # bpy.context.active_object.name += "_custom_obj"
    # plane_custom_obj = bpy.context.active_object
    # plane_custom_obj.scale = (0.1, 0.1, 0.1)
    # plane_custom_obj.rotation_euler[0] += radians(90)
    # bpy.ops.object.transform_apply(rotation=True)
    # bpy.ops.object.transform_apply(scale=True)

    # create cirle as custom obj for bone
    bpy.ops.mesh.primitive_circle_add(
        radius=1, enter_editmode=False, align="WORLD", location=(0, 0, 0)
    )
    circle_custom_obj = bpy.context.active_object
    bpy.context.active_object.name += "_custom_obj"
    circle_custom_obj.scale = (0.1, 0.1, 0.1)
    circle_custom_obj.rotation_euler[0] += radians(90)
    bpy.ops.object.transform_apply(rotation=True)
    bpy.ops.object.transform_apply(scale=True)

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.fill_grid(span=1, offset=11, use_interp_simple=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    # ===========================================================
    # create armature
    bpy.ops.object.armature_add(
        enter_editmode=False, align="WORLD", location=(0, 0, 0), scale=(1, 1, 1)
    )
    arm = bpy.context.active_object
    arm.name = name

    bones = {
        # bone name : [head, tail, parent, layer, custom_obj]
        "root": [
            (0, 0, 0),
            (0, 1, 0),
            None,
            0,
            circle_custom_obj,
            # plane_custom_obj,
        ],
        "top_left": [
            (-1, 0, 1),
            (-1, 1, 1),
            "root",
            0,
            circle_custom_obj,
        ],
        "bottom_right": [
            (1, 0, -1),
            (1, 1, -1),
            "root",
            0,
            circle_custom_obj,
        ],
        "top_right": [
            (1, 0, 1),
            (1, 1, 1),
            None,
            1,
            None,
        ],
        "bottom_left": [
            (-1, 0, -1),
            (-1, 1, -1),
            None,
            1,
            None,
        ],
    }

    # ===========================================================

    bpy.ops.object.mode_set(mode="EDIT")

    # delete exising bone in created armature
    for i in arm.data.bones:
        i = arm.data.edit_bones[i.name]
        arm.data.edit_bones.remove(i)

    # create bones, rename, displace, assign parent
    for bone, param in bones.items():
        make_bone(arm, bone, param[2], param[0], param[1])

    # adding bones to layer
    bpy.ops.object.mode_set(mode="POSE")

    for bone, param in bones.items():
        context_bone = bpy.context.object.data.bones[bone]
        context_bone.layers[param[3]] = True
        # disable all the other layers but layer[0]
        for cnt in range(0, 32):
            if cnt != param[3]:
                context_bone.layers[cnt] = False

    # ===========================================================

    # make constraints, set color to bone group
    bpy.ops.object.mode_set(mode="POSE")

    constraints = {
        "root": [
            ["LIMIT_LOCATION", "(max, min Y: 0)"],
            ["LIMIT_ROTATION", "(all 0)"],
        ],
        "top_left": [
            ["LIMIT_LOCATION", "(max, min Y: 0)"],
            ["LIMIT_ROTATION", "(all 0)"],
        ],
        "bottom_right": [
            ["LIMIT_LOCATION", "(max, min Y: 0)"],
            ["LIMIT_ROTATION", "(all 0)"],
        ],
        "top_right": [
            ["COPY_LOCATION", ["top_left", "z"]],
            ["COPY_LOCATION", ["bottom_right", "x"]],
        ],
        "bottom_left": [
            ["COPY_LOCATION", ["top_left", "x"]],
            ["COPY_LOCATION", ["bottom_right", "z"]],
        ],
    }

    # create new bone group
    bone_group = arm.pose.bone_groups
    bone_group_name = "Custom Bone Group"
    bone_group.new(name=bone_group_name)
    # set color to bone group
    bone_group.active.color_set = "CUSTOM"
    bone_group.active.colors.normal = (color[0], color[1], color[2])

    for bone, constr in constraints.items():
        p_bone = arm.pose.bones[bone]

        # assign bone to bone group
        p_bone.bone_group = bone_group.get(bone_group_name)

        for c in constr:
            p_bone.constraints.new(c[0])
            constr_name = get_constrain_name(p_bone.name, arm)
            constraint = p_bone.constraints[constr_name]
            if c[0] == "LIMIT_LOCATION":
                constraint.use_min_y = True
                constraint.min_y = 0

                constraint.use_max_y = True
                constraint.max_y = 0

            if c[0] == "LIMIT_ROTATION":
                constraint.use_limit_x = True

                constraint.use_limit_y = True
                constraint.use_limit_z = True

            if c[0] == "COPY_LOCATION":
                constraint.target = bpy.data.objects[arm.name]
                constraint.subtarget = c[1][0]

                constraint.use_x = False
                constraint.use_y = False
                constraint.use_z = False

                if c[1][1] == "x":
                    constraint.use_x = True
                if c[1][1] == "y":
                    constraint.use_y = True
                if c[1][1] == "z":
                    constraint.use_z = True

            constraint.show_expanded = False

    # ===========================================================

    # add plane
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False)

    bpy.context.active_object.name = f"{name}_bb"
    plane = bpy.context.active_object
    plane.rotation_euler[0] += radians(90)
    bpy.ops.object.transform_apply(rotation=True)

    # ===========================================================

    # creating material
    material_basic = bpy.data.materials.new(name=name)
    material_basic.use_nodes = True
    plane.active_material = material_basic
    principled_node = material_basic.node_tree.nodes.get("Principled BSDF")
    principled_node.inputs[0].default_value = (color[0], color[1], color[2], 1)
    # alpha = 0.3
    principled_node.inputs[21].default_value = 0.3

    # add Alpha Blend to material
    material_basic.blend_method = "BLEND"

    # ===========================================================

    # add vertex group
    for k, v in bones.items():
        group = plane.vertex_groups.new(name=k)
        if v[4] != None:
            arm.pose.bones[k].custom_shape = bpy.data.objects[v[4].name]

    # Assign vertices to vertex group
    for vert in plane.data.vertices:
        vert_loc = plane.matrix_world @ vert.co

        for k, v in bones.items():
            if vert_loc[0] == v[0][0] and vert_loc[2] == v[0][2]:
                group = plane.vertex_groups[k]
                group.add([vert.index], 1.0, "ADD")

    # ===========================================================

    # add armature modifier
    arm_mod = plane.modifiers.new(type="ARMATURE", name="armature")
    arm_mod.object = arm

    # ===========================================================
    # link objects to collection
    import_video.link_to_collection(arm_coll, arm)
    # import_video.link_to_collection(bone_shape_coll, plane_custom_obj)
    import_video.link_to_collection(bone_shape_coll, circle_custom_obj)
    import_video.link_to_collection(arm_coll, plane)

    # plane_custom_obj.hide_set(True)
    circle_custom_obj.hide_set(True)

    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    # bpy.ops.object.mode_set(mode="POSE")


# # # # ===========================================================
# # # # ===========================================================
# # # bounding_box_set_up("name lolk", 123)
