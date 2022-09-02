# import collections
import bpy
from math import radians
from . import collection_functional
import os

os.system("cls")

# ===========================================================
def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)


def parent_lookup(coll):
    parent_lookup = {}
    for coll in traverse_tree(coll):
        for c in coll.children.keys():
            parent_lookup.setdefault(c, coll)
    return parent_lookup


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


def get_new_name(name_to_check):
    obj_names = [obj.name for obj in bpy.data.objects]
    new_name = ""
    # if there's no obj with the name, keep name as is
    if name_to_check not in obj_names:
        new_name = name_to_check
    else:
        for i in range(1, 40):
            i = f"{i:003}"
            new_name_check = f"{name_to_check}.{i}"
            if (new_name_check in obj_names) == False:
                new_name = new_name_check
                break
    return new_name


# ===========================================================


def bounding_box_set_up(self, name, color):

    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    # get active collection
    target_collection = bpy.context.view_layer.active_layer_collection.collection
    print(target_collection.name)
    print(target_collection.get("class_id"))
    if target_collection.get("class_id") != None:
        print("ino")

        name = get_new_name(name)

        # create collections
        arm_coll = collection_functional.create_collection(name)
        bone_shape_coll = collection_functional.create_collection("Bone Shapes", True)

        # ===========================================================
        # create plane as custom obj for bone
        if "Plane_Custom_Obj" not in bpy.data.objects:
            bpy.ops.mesh.primitive_plane_add(
                size=2, enter_editmode=False, align="WORLD", location=(0, 0, 0)
            )

            bpy.context.active_object.name = "Plane_Custom_Obj"
            plane_custom_obj = bpy.context.active_object
            plane_custom_obj.scale = (0.1, 0.1, 0.1)
            plane_custom_obj.rotation_euler[0] += radians(90)
            bpy.ops.object.transform_apply(rotation=True)
            bpy.ops.object.transform_apply(scale=True)
        else:
            plane_custom_obj = bpy.data.objects["Plane_Custom_Obj"]

        # create cirle as custom obj for bone
        if "Circle_Custom_Obj" not in bpy.data.objects:
            bpy.ops.mesh.primitive_circle_add(
                radius=1, enter_editmode=False, align="WORLD", location=(0, 0, 0)
            )
            circle_custom_obj = bpy.context.active_object
            bpy.context.active_object.name = "Circle_Custom_Obj"
            circle_custom_obj.scale = (0.1, 0.1, 0.1)
            circle_custom_obj.rotation_euler[0] += radians(90)
            bpy.ops.object.transform_apply(rotation=True)
            bpy.ops.object.transform_apply(scale=True)

            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.fill_grid(span=1, offset=11, use_interp_simple=False)
            bpy.ops.object.mode_set(mode="OBJECT")
        else:
            circle_custom_obj = bpy.data.objects["Circle_Custom_Obj"]

        # ===========================================================
        # create armature
        bpy.ops.object.armature_add(
            enter_editmode=False, align="WORLD", location=(0, 0, 0), scale=(1, 1, 1)
        )
        arm = bpy.context.active_object
        arm_name = name
        # arm_name = get_new_name(name)

        arm.name = arm_name
        arm.data.name = arm_name

        bones = {
            # bone name : [head, tail, parent, layer, custom_obj]
            "root": [
                (0, 0, 0),
                (0, 1, 0),
                None,
                0,
                plane_custom_obj,
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

        plane_name = f"{name}_plane"

        bpy.context.active_object.name = plane_name
        plane = bpy.context.active_object
        plane.rotation_euler[0] += radians(90)
        plane.location = (0, 0, 0)
        bpy.ops.object.transform_apply(rotation=True)

        plane.parent = arm

        # ===========================================================

        # creating material
        mat_name = f"{name}_mat"
        material_basic = bpy.data.materials.new(name=mat_name)
        material_basic.use_nodes = True
        plane.active_material = material_basic
        principled_node = material_basic.node_tree.nodes.get("Principled BSDF")
        principled_node.inputs[0].default_value = (color[0], color[1], color[2], 1)
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
        collection_functional.link_object_to_collection(arm_coll, arm)
        collection_functional.link_object_to_collection(
            bone_shape_coll, plane_custom_obj
        )
        collection_functional.link_object_to_collection(
            bone_shape_coll, circle_custom_obj
        )
        collection_functional.link_object_to_collection(arm_coll, plane)

        plane_custom_obj.hide_set(True)
        circle_custom_obj.hide_set(True)

        bpy.ops.object.select_all(action="DESELECT")
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        # bpy.ops.object.mode_set(mode="POSE")

        # ===========================================================

        # moveve bounding_box collection to active collection
        C = bpy.context

        # Get all collections of the scene and their parents in a dict
        coll_scene = C.scene.collection
        coll_parents = parent_lookup(coll_scene)

        active_coll = bpy.data.collections[arm_coll]

        # Get parent of *active_coll*
        active_coll_parent = coll_parents.get(active_coll.name)

        if active_coll_parent:
            active_coll_parent.children.unlink(active_coll)
            target_collection.children.link(active_coll)

        # ===========================================================

        # good_col = []
        # for col in bpy.data.collections:
        #     if col.get("class_id") != None:
        #         good_col.append(col)

        # if target_collection.get("class_id") == None:
        #     # if there is collection with custom prop, but is not selected
        #     if len(good_col) != 0:
        #         # ('DEBUG', 'INFO', 'OPERATOR', 'PROPERTY', 'WARNING', 'ERROR', 'ERROR_INVALID_INPUT', 'ERROR_INVALID_CONTEXT', 'ERROR_OUT_OF_MEMORY')
        #         self.report(
        #             {"ERROR"},
        #             f"'{target_collection.name}' doesn't have custom prop, select blue collection",
        #         )
        #     else:
        #         self.report(
        #             {"ERROR"},
        #             f"Create collection with 'Add New Class ID' first and place collection '{arm_coll}' there",
        #         )
        # del good_col

        # # Get all collections of the scene and their parents in a dict
        # coll_scene = bpy.context.scene.collection
        # coll_parents = parent_lookup(coll_scene)
        # # print(f"coll_scene   {coll_scene} {type(coll_scene)} ")
        # print(f"coll_parents {coll_parents}   {type(coll_parents)} ")
        # for k, v in coll_parents.items():
        #     print()
        #     print(f"\t {k}")
        #     print(f"\t {v.name}")

        #     # getting colletion with custom props
        #     colls = []
        #     for col in bpy.data.collections:
        #         if col.get("class_id") != None:
        #             colls.append(col)

        #     for i in colls:
        #         print(i)

        #     print()
        #     print(f"len(colls) {len(colls)}")

        #     # if only one collections has custom prop assign bb to it
        #     if len(colls) == 1:
        #         target_collection = colls[0]

        #     # Get all collections of the scene and their parents in a dict
        #     coll_scene = bpy.context.scene.collection
        #     coll_parents = parent_lookup(coll_scene)
        #     print(f"coll_scene   {coll_scene} {type(coll_scene)} ")
        #     print(f"coll_parents {coll_parents} {type(coll_parents)} ")
        #     for k, v in coll_parents.items():
        #         print()
        #         print(f"\t k {k} {type(k)} ")
        #         print(f"\t v {v} {type(v)} ")
    else:
        good_col = []
        for col in bpy.data.collections:
            if col.get("class_id") != None:
                good_col.append(col)

        if target_collection.get("class_id") == None:
            # if there is collection with custom prop, but is not selected
            if len(good_col) != 0:
                # ('DEBUG', 'INFO', 'OPERATOR', 'PROPERTY', 'WARNING', 'ERROR', 'ERROR_INVALID_INPUT', 'ERROR_INVALID_CONTEXT', 'ERROR_OUT_OF_MEMORY')
                self.report(
                    {"ERROR"},
                    f"'{target_collection.name}' doesn't have custom prop, select blue collection",
                )
            else:
                self.report(
                    {"ERROR"},
                    f"Create collection with 'Add New Class ID' first",
                )
        del good_col


# # # # # ===========================================================
# # # # # ===========================================================
# # # # bounding_box_set_up("name lolk", 123)
