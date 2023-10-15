import bpy
import mathutils
from . import boneFunctions as bnf


def create_ribbon(obj, selection, wgt=None):
    """ creates a ribbon like system chain on a chain of bones """
    # references for easier bone management
    Pbone = obj.pose.bones
    Ebone = obj.data.edit_bones

    print(selection)

    # get the bone list length
    l = len(selection)

    #  rb bones
    ribbonBones = []

    # for each bone in the chain....
    print(f'[URT]:> bones selected for operation{selection}')

    # create a new list for
    # get new name for the ribbon controllers
    newName = selection[0]

    for bone in selection:
        # reset parent
        Ebone[bone].parent = None

        # get bone size
        boneLength = Ebone[bone].length / 4

        # if tail of chain, spawn bone only on its tail
        if bone == selection[l - 1]:
            rbBone = Ebone.new('RB_' + newName)
            rbBone.head = Ebone[bone].head
            rbBone.tail = rbBone.head + mathutils.Vector([0, 0, boneLength])
            rbBone.parent = Ebone[bone].parent
            # append to list
            ribbonBones.append(rbBone.name)
            # remove from deform
            rbBone.use_deform = False
            # crate tail rb bone
            rbBone = Ebone.new('RB_' + newName)
            rbBone.head = Ebone[bone].tail
            rbBone.tail = rbBone.head + mathutils.Vector([0, 0, boneLength])
            rbBone.parent = Ebone[bone].parent
            # append to list
            ribbonBones.append(rbBone.name)
            # remove from deform
            rbBone.use_deform = False

        # spawn a ribbon bone(RB_bone) on its head, and its tail and parent them to the og bone parent
        else:
            rbBone = Ebone.new('RB_' + newName)
            rbBone.head = Ebone[bone].head
            rbBone.tail = rbBone.head + mathutils.Vector([0, 0, boneLength])
            rbBone.parent = Ebone[bone].parent
            ribbonBones.append(rbBone.name)
            # remove from deform
            rbBone.use_deform = False

    print(ribbonBones)
    # append the new created bones (name) to a new list named rbBones ( they should be in order of chain...)

    # switch to pose mode
    bpy.ops.object.mode_set(mode='POSE')
    # for each bone in the ribbon
    # iteration variable

    for i, bone in enumerate(selection):

        # create a copy location constraint to the head rb bone

        constraint = Pbone[bone].constraints.new('COPY_LOCATION')
        constraint.target = obj
        constraint.subtarget = ribbonBones[i]
        constraint.target_space = 'WORLD'
        constraint.owner_space = 'WORLD'

        constraint = Pbone[bone].constraints.new('STRETCH_TO')
        constraint.target = obj
        constraint.subtarget = ribbonBones[i + 1]

        # add widgets
        if wgt:
            Pbone[ribbonBones[i]].custom_shape = bpy.data.objects[wgt]
            Pbone[ribbonBones[i + 1]].custom_shape = bpy.data.objects[wgt]

    return ribbonBones


def create_wrapBones(armature, selection, targetMesh, offsetBone=None):
    #force set to edit mode just in case
    bpy.ops.object.mode_set(mode='EDIT')
    # definitions for easier access

    pBones = armature.pose.bones
    eBones = armature.data.edit_bones
    newSelection = []
    for bone in selection:
        newSelection.append(bone)

    # for each of the selected bones

    for bone in newSelection:
        # create a new wrap bone
        wrapBone = bnf.create_dupeBones(armature, eBones[bone], "WRAP_")[0]

        # change bone reference to its name
        # set armature to pose mode
        bpy.ops.object.mode_set(mode='POSE')

        # add offset constraint to wrap bone
        constraint = pBones[wrapBone].constraints.new('CHILD_OF')
        constraint.target = armature
        constraint.subtarget = offsetBone

        # add shrinkwrap mod
        constraint = pBones[wrapBone].constraints.new('SHRINKWRAP')
        constraint.target = targetMesh
        constraint.shrinkwrap_type = 'TARGET_PROJECT'

        # parent og bone to wrap bone
        constraint = pBones[bone].constraints.new('CHILD_OF')
        constraint.target = armature
        constraint.subtarget = wrapBone

        # set armature to pose mode
        bpy.ops.object.mode_set(mode='EDIT')
class create_RibbonOperator(bpy.types.Operator):
    """creates  a ribbon chain from a chain of bones """
    bl_idname = "create.ribbon"
    bl_label = "create ribbon bones"

    wgt: bpy.props.StringProperty()
    useWrap: bpy.props.BoolProperty(default=False)
    wrapMesh: bpy.props.StringProperty()
    offsetBone: bpy.props.StringProperty()

    def execute(self, context):

        if context.selected_bones:
            ribbonBOnes = create_ribbon(context.active_object, bnf.sort_BoneOrder(context.selected_bones), self.wgt)
            if self.useWrap:
                create_wrapBones(context.active_object, ribbonBOnes, context.scene.objects.get(self.wrapMesh), self.offsetBone)
                pass

            return {'FINISHED'}


        else:
            self.report({'INFO'}, "something wrong matey?")
            return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def draw(self, context):
        layout = self.layout
        layout.label(text="widget")
        layout.prop_search(self, "wgt", bpy.data, "objects", text="")
        layout.prop(self, 'useWrap', text="use wrap mesh")
        if self.useWrap:
            layout.label(text="target mesh")
            layout.prop_search(self, "wrapMesh", bpy.data, "objects", text="")
            layout.label(text="optional offet bone")
            layout.prop_search(self, "offsetBone", context.object.data, "bones", text="")