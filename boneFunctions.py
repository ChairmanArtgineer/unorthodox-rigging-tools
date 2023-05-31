import bpy
import mathutils

def create_dupeBones(obj,selection, prefix, newp):
    """duplicates a bone or bone chain and returns the names of new bones"""
    if obj.type == 'ARMATURE' and obj.mode == 'EDIT':

        # if single bone append to list
        if isinstance(selection, bpy.types.EditBone):
            selectedBones = []
            selectedBones.append(selection)
        else:
            # equal list
            selectedBones = selection

        newBones = []
        for bone in selectedBones:

            # create new bone with prefix
            new_bone_name = prefix + bone.name
            new_bone = obj.data.edit_bones.new(new_bone_name)
            # copy rest data from bone to new bone
            new_bone.head = bone.head
            new_bone.tail = bone.tail
            new_bone.roll = bone.roll
            new_bone.use_deform = False
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
            newBones.append(new_bone.name)
        # update refs
        obj.update_from_editmode()
        return newBones
        # select only the new chain


def add_follow(obj,selection, Prefix, space):
    if isinstance(selection, bpy.types.EditBone):
        selectedBones = []
        selectedBones.append(selection)
    else:
        # equal list
        selectedBones = selection
    for bone in selectedBones:
        constraint = bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = Prefix + "follow"
        constraint.target = obj
        constraint.subtarget = Prefix + bone.name
        constraint.target_space = space
        constraint.owner_space = space


def add_IK(obj, selection):
    """creates an ik chain from 3 bones and adds a pole bone"""
    pbone = obj.pose.bones

    ikTarget = find_Tail(selection)
    ikBone = ikTarget.parent
    ikEnd = ikBone.parent

    # clear parent for ik target
    ikTarget.parent = None

    # get a position for the pole bone
    barycenter = (ikTarget.head + ikBone.head + ikEnd.head) / 3
    fkPole = (ikBone.head - barycenter) * 4
    fkPole = mathutils.Matrix.Translation(fkPole) @ (ikBone.matrix)

    # place pole bone
    ikPole = obj.data.edit_bones.new(ikEnd.name + "_Pole")

    ikPole.head = (0, 0, 0)
    ikPole.tail = (0, 0, 1)
    ikPole.matrix = fkPole
    ikPole.tail = ikPole.head + mathutils.Vector((0, 0, 1))
    ikPole.use_deform = False
    print("pole vector generated:", ikPole.name)

    # calculate pole angle
    # def get_pole_angle(base_bone, ik_bone, pole_location):
    pole_normal = (ikBone.tail - ikEnd.head).cross(ikPole.matrix.translation - ikEnd.head)
    projected_pole_axis = pole_normal.cross(ikEnd.tail - ikEnd.head)
    poleAngle = ikEnd.x_axis.angle(projected_pole_axis)

    if ikEnd.x_axis.cross(projected_pole_axis).angle(ikEnd.tail - ikEnd.head) < 1:
        poleAngle = -poleAngle
    # poleAngle = (180 * poleAngle) // 3.14159265359
    print("pole angle generated:", (180 * poleAngle) // 3.14159265359)

    # set the pole bone to its name for later use
    ikPole = ikPole.name
    ikTarget = ikTarget.name
    ikEnd = ikEnd.name
    ikBone = ikBone.name

    # set pose mode

    bpy.ops.object.mode_set(mode='POSE')

    # copy transforms for the ik bones

    # get the dupebones from names to pose bones         //objref

    # reset ik references
    ikBone = pbone[ikBone]
    ikEnd = pbone[ikEnd]
    ikTarget = pbone[ikTarget]
    ikPole = pbone[ikPole]

    # create ik constraint
    constraint = ikBone.constraints.new('IK')
    constraint.target = obj
    constraint.subtarget = ikTarget.name
    constraint.pole_target = obj
    constraint.pole_subtarget = ikPole.name
    constraint.chain_count = 2
    constraint.pole_angle = poleAngle


def find_Head(selection):
    for bone in selection:
        if bone.parent in selection:
            pass
        else:
            print("found head of the chain", bone.name)
            return bone


import bpy
def find_Tail(selection):
    for bone in selection:
        if not any(bone.children):
            print("found tail of the chain", bone.name)
            return bone
        else:
            if not any( bone in selection for bone in bone.children):
                print("found tail of the chain", bone.name)
                return bone

def find_BonesByName(obj,selection, type):
    foundBones = []
    for name in selection:
        foundBones.append(obj.pose.bones[name])
    return foundBones
def select_ByConstraint(selection, cname):
    bones = []
    for bone in selection:
        if cname in bone.constraints:
            print("keep")
        else:
            bpy.context.active_object.data.bones[bone.name].select = False
            bones.apend(bone)


