import bpy

class parenting_props(bpy.types.PropertyGroup):
    ConnectBones : bpy.props.BoolProperty(
        name="connect",
        default="",
        )
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

class VIEW3D_parenting_UI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "MAIN_UI"
    bl_category = "anti autodesk tools"
    bl_label = "parent related"
   # bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        if (bpy.context.mode == 'POSE'):
            layout = self.layout
            col = layout.column(align=True)
            col.row().label(text="shelf ", translate=False)
            col.operator('parent.posemode',
                         icon='BONE_DATA')
            col.prop(context.scene, 'ConnectBones')
        pass

BlenderClasses = [
VIEW3D_parenting_UI,
parenting_props

]
def register():
    for blender_class in BlenderClasses:
        bpy.utils.register_class(blender_class)
    bpy.types.Scene.parentProps = bpy.props.PointerProperty(
        type=parenting_props)



def unregister():
    del bpy.types.Scene.parentProps
    for blender_class in BlenderClasses:
        bpy.utils.unregister_class(blender_class)






