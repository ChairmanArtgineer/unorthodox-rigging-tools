import bpy




def parentingfunction(setconnected):

    slct_bones = bpy.context.selected_pose_bones
    act_bone = bpy.context.active_pose_bone
    if(slct_bones is not None):
        bpy.ops.object.mode_set(mode='EDIT')
        slct_bones = bpy.context.selected_bones
        act_bone = bpy.context.active_bone

    for bone in slct_bones:

        if act_bone.name == bone.name:
            pass
        else:
            bone.parent = act_bone
            bone.use_connect = setconnected
    bpy.ops.object.mode_set(mode='POSE')


class ParentPoseMode(bpy.types.Operator):
    """sets bone parents from pose mode"""
    bl_idname = "parent.posemode"
    bl_label = "parent from posemode"

    bpy.types.Scene.ConnectBones = bpy.props.BoolProperty(
        name='Connected')
    def execute(self, context):
        parentingfunction(context.scene.ConnectBones)

        return {'FINISHED'}

bpy.types.Scene.Cname = bpy.props.StringProperty()






