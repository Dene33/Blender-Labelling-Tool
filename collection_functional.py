import bpy


def make_collection(coll_name):
    collection = bpy.data.collections.new(coll_name)
    bpy.context.scene.collection.children.link(collection)


def create_collection(coll_name, create_new=False):
    coll = None
    if coll_name not in bpy.data.collections:
        make_collection(coll_name)
        coll = coll_name
    # rename collection if it already exists
    else:
        if create_new == False:
            print(f"[-] collection named {coll_name} already exists")
            for i in range(1, 40):
                i = f"{i:003}"
                new_coll_name = f"{coll_name}.{i}"
                if (new_coll_name in bpy.data.collections) == False:
                    coll_name = new_coll_name
                    make_collection(coll_name)
                    coll = coll_name
                    break
        if create_new == True:
            coll = coll_name
    return coll


# ===============================================================


def link_to_collection(cam_coll_name, obj):
    for coll in obj.users_collection:
        coll.objects.unlink(obj)
    coll_target = bpy.context.scene.collection.children.get(cam_coll_name)
    coll_target.objects.link(obj)
