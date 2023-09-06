import bpy
import mathutils
import math

def create_dupeBones(obj,selection, prefix):
    """duplicates a bone or bone chain and returns the names of new bones
    :param obj: active armature
    :param selection: list of bones in editBone type
    :param prefix: prefix for the new bones
    :return: the list of new bones generated
    """
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
            if bone.parent:
                if prefix + bone.parent.name in obj.data.bones:
                    new_bone.parent = obj.data.edit_bones[prefix + bone.parent.name]
                    new_bone.use_connect = bone.use_connect
                else:
                    new_bone.parent = obj.data.edit_bones[bone.parent.name]

            newBones.append(new_bone.name)
        # update refs
        obj.update_from_editmode()
        return newBones
        # select only the new chain


def add_follow(obj,selection, Prefix, space, type):
    """
    adds a followw
    :param obj:
    :param selection:
    :param Prefix:
    :param space:
    """
    if isinstance(selection, bpy.types.EditBone):
        selectedBones = []
        selectedBones.append(selection)
    else:
        # equal list
        selectedBones = selection
    for bone in selectedBones:
        if type == "COPY_TRANSFORMS":
            constraint = bone.constraints.new('COPY_TRANSFORMS')
            constraint.name = Prefix + "follow"
            constraint.target = obj
            constraint.subtarget = Prefix + bone.name
            constraint.target_space = space
            constraint.owner_space = space
        if type == "CHILD_OF":
            constraint = bone.constraints.new('CHILD_OF')
            constraint.target = obj
            constraint.subtarget = Prefix + bone.name


def add_widgetToBones(selection, wgtName=None, wgtScale=None, wgtPos=None, wgtRot=None):
    """adds a widged if inserted a objectname"""
    poseBones = []
    if isinstance(selection, bpy.types.PoseBone):
        poseBones.append(selection)
    else:
        poseBones = selection
    if wgtName:
        for bone in poseBones:
            if wgtName in bpy.data.objects:
                print("ahoy matey!, custom mesh found")
                bone.custom_shape = bpy.data.objects[wgtName]

            else:
                print("arrr... not a correct name  for ", wgtName)
                break
    else:
        for bone in poseBones:
            print("arr... no widget on bones", bone.name)
            bone.custom_shape = None
            break
    if wgtScale:
        for bone in poseBones:
            for axis in range(3):
                bone.custom_shape_scale_xyz[axis] = wgtScale[axis]
    if wgtPos:
        for bone in poseBones:
            for axis in range(3):
                bone.custom_shape_translation[axis] = wgtPos[axis]
    if wgtRot:
        for bone in poseBones:
            for axis in range(3):
                bone.custom_shape_rotation_euler[axis] = math.radians(wgtRot[axis])

        pass
def add_IK(obj, selection,ikWgt = None,poleWgt = None):
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

    # update first

    # update refernces
    obj.update_from_editmode()
    #switch modes
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

    #add widget to target and pole
    add_widgetToBones(ikTarget,ikWgt,(1/2,1/2,1/2))
    add_widgetToBones(ikPole,poleWgt,(1/4,1/4,1/4))
    return ikPole



def find_Head(selection):
    """
    finds the head in a chain of bones
    :param selection: list of bones in a chain
    :return: chain head
    """
    for bone in selection:
        if bone.parent in selection:
            pass
        else:
            print("found head of the chain", bone.name)
            return bone



def find_Tail(selection):
    """
    finds the tail bone in a chain of bones
    :param selection: list of bones in a chain
    :return: the tail of the chain
    """
    for bone in selection:
        if not any(bone.children):
            print("found tail of the chain", bone.name)
            return bone
        else:
            if not any( bone in selection for bone in bone.children):
                print("found tail of the chain", bone.name)
                return bone


def find_BonesByName(obj, names,type):
    """
    finds bones by names given and returns them in a list
    :param obj: active armature
    :param names: list of bone names
    :param type: pose or edit type bones to return
    :return: list of bones in the specified type
    """
    # update shit this  function is so good
    list = []
    if type == 'POSE':

        for i in range(len(names)):
            list.append(obj.pose.bones[names[i]])

    if type == 'EDIT':
        for i in range(len(names)):
            list.append(obj.data.edit_bones[names[i]])

    return list


def find_closestBones(obj, selection, target, nBones):
    """
    find the closest bones to target bone
    :param obj: active armature
    :param selection: list of bones by name
    :param target: target bone by name
    :param nBones: number of the closest bones to return
    :return: list of the closest bones sorted by order
    """
    # update just for safety
    obj.update_from_editmode()

    if target in obj.data.bones:
        targetBone = obj.data.bones[target]
        # Create a dictionary to store bone names and their distances
        boneDistances = {}

        # Iterate through all bones in the obj
        for bone in selection:
            if bone != target:
                # Calculate the distance between the target bone's head and the current bone's head
                distance = (obj.data.bones[bone].head - targetBone.head).length
                boneDistances[obj.data.bones[bone].name] = distance

        # Sort the dictionary by distances
        sortedBones = sorted(boneDistances.items(), key=lambda x: x[1])

        # print the bones in console for later debugging
        print("yar! the closest" + str(nBones) + "to " + target + "are :")
        for i in range(0, nBones):
            print(sortedBones[i][0])

        return [bone[0] for bone in sortedBones[:nBones]]
        # Print the three closest bone names

    else:
        print("grr.... target bone not found in armature...")
        # Get the three closest bones


def get_namesByBone(bones):
    """
    gets the names of desired bones in a list
    :param bones: list of bones in any type
    :return: list of bone names
    """
    names = []
    for i in range (len(bones)):
        names.append(bones[i].name)
    return names
def select_ByConstraint(selection, cname):
    bones = []
    for bone in selection:
        if cname in bone.constraints:
            print("keep")
        else:
            bpy.context.active_object.data.bones[bone.name].select = False
            bones.append(bone)


def set_mirrorByPos(selection, margin=0.01):
    """
    auto sets mirror based on bone positions (very experimental)

    :param selection: list of bones
    :param margin: margin from the center to start naming
    :return: bones from left side and bones from right side
    """
    # create a list for the left side bones and right side
    leftBones = []
    rightBones = []

    # autoasign LEFT suffix to bones on left side of the mesh and assign the bones to their lists
    for bone in selection:
        if bone.head.x > margin:
            bone.name += ".L"
            leftBones.append(bone)

        elif bone.head.x < margin:
            rightBones.append(bone)

    # rename bones based on position

    for Rbone in rightBones:
        for Lbone in leftBones:
            if Rbone.head.x == Lbone.head.x * -1:
                Rbone.name = Lbone.name[:-2] + ".R"
    return [leftBones, rightBones]

def set_childofInverse(obj,selection,cname):
    """
    resets the inverse of a specified chilf of constraint in a chain of bones
    :param obj: active armature
    :param selection: list of bones in posebone type
    :param cname: name of the childof constraint
    """
    for bone in selection:
        for c in bone.constraints:
            if c.type == "CHILD_OF" and c.subtarget and c.name == cname:
                target = c.subtarget
                c.inverse_matrix = obj.pose.bones[target].matrix.inverted()


def sort_BoneOrder(selection):
    newSelection = []
    tailBone = find_Tail(bpy.context.selected_bones)
    newSelection.append(tailBone.name)

    for i in range(1, len(selection)):
        if tailBone.parent:
            tailBone = tailBone.parent
            newSelection.insert(0, tailBone.name)
        else:
            newSelection.insert(0, tailBone.name)
    return newSelection