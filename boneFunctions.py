import bpy

def create_dupeBones(obj,selection, prefix, newp):
    if obj.type == 'ARMATURE' and obj.mode == 'EDIT':
        # iterate through each selected bone
        for bone in selection:
            # create new bone with prefix
            new_bone_name = prefix + bone.name
            new_bone = obj.data.edit_bones.new(new_bone_name)
            # copy rest data from bone to new bone
            new_bone.head = bone.head
            new_bone.tail = bone.tail
            new_bone.roll = bone.roll
            if newp:
                if bone.parent:
                    new_bone.parent = obj.data.edit_bones[prefix + bone.parent.name]
                    new_bone.use_connect = bone.use_connect
                else:
                    pass
            else:
                if bone.parent:
                    new_bone.parent = obj.data.edit_bones[bone.parent.name]
                    new_bone.use_connect = bone.use_connect
                    # select only the new chain


def create_FkSimple(obj,selection, prefix, cname):
    selectedBones = []
    selectedBones.append(selection)
    for bone in selectedBones:
        constraint = bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = cname
        constraint.target = obj
        constraint.subtarget = prefix + bone.name
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'


def find_Head(selection):
    for bone in selection:
        if bone.parent in selection:
            pass
        else:
            print("found head of the chain", bone.name)
            return bone


def find_Tail(selection):
    for bone in selection:
        if bone.child in selection:
            pass
        else:
            print("found tail of the chain", bone.name)


def select_ByConstraint(selection, cname):
    for bone in selection:
        if cname in bone.constraints:
            print("keep")
        else:
            bpy.context.active_object.data.bones[bone.name].select = False

