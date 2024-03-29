

import bpy 
import mathutils
Vector = mathutils.Vector
from . import boneFunctions as bnf

def create_muscle(muscleBone, obj,wgt=None):

    #just update the fkn references
    bpy.context.object.update_from_editmode()
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.object.mode_set(mode='EDIT')

    #input a bone, this is the muscle bone
    muscleBone = obj.data.edit_bones[muscleBone]
    muscleLength = muscleBone.length



    #register said bone with head,tail and name
    origin = muscleBone.head
    insertion = muscleBone.tail
    muscleName = "MSC_" + muscleBone.name
    #add origin and insertion bone (no orientation)
    muscleOrigin = muscleName + "_muscleOrigin"
    muscleInsertion = muscleName + "_muscleInsertion"
    bpy.ops.armature.bone_primitive_add(name = muscleOrigin)
    bpy.ops.armature.bone_primitive_add(name = muscleInsertion)

    muscleOrigin = bpy.context.active_object.data.edit_bones[muscleOrigin]
    muscleInsertion = bpy.context.active_object.data.edit_bones[muscleInsertion]

    muscleOrigin.head = origin
    muscleOrigin.tail = origin  + Vector([0,0,muscleLength/4])

    muscleInsertion.head = insertion
    muscleInsertion.tail = insertion  + Vector([0,0,muscleLength/4])


    #set said bone head to the middle point of itself
    muscleBone.head = (origin + insertion)/2
    #create the muscle tip and base bones
    muscleBase = muscleName + "_muscleBase"
    muscleTip = muscleName + "_muscleTip"
    bpy.ops.armature.bone_primitive_add(name = muscleBase)
    bpy.ops.armature.bone_primitive_add(name = muscleTip)
    muscleBase = bpy.context.active_object.data.edit_bones[muscleBase]
    muscleTip = bpy.context.active_object.data.edit_bones[muscleTip]

    muscleBase.head = muscleOrigin.head
    muscleBase.tail = muscleOrigin.tail
    muscleBase.parent = muscleOrigin

    muscleTip.head = muscleInsertion.head
    muscleTip.tail = muscleInsertion.tail
    muscleTip.parent = muscleOrigin


    #create the muscle  driver bone (duplicate muscle bone)

    muscleDriver = muscleName + "_muscleDriver"
    muscleOffset = muscleName + "_muscleOffset"
    bpy.ops.armature.bone_primitive_add(name = muscleDriver)
    bpy.ops.armature.bone_primitive_add(name = muscleOffset)

    muscleOffset = bpy.context.active_object.data.edit_bones[muscleOffset]
    muscleDriver = bpy.context.active_object.data.edit_bones[muscleDriver]

    muscleOffset.head = muscleBone.head
    muscleOffset.tail = muscleOffset.head + Vector([0,0,muscleLength/4])

    muscleDriver.head = muscleBone.head
    muscleDriver.tail = muscleBone.tail

    muscleBone.parent = muscleDriver
    muscleDriver.parent = muscleOffset
    muscleOffset.parent = muscleOrigin
    print(muscleTip.name  + muscleOffset.name)
    #switch to pose mode dear god please....
    muscleTip = muscleTip.name
    muscleOffset = muscleOffset.name
    muscleDriver = muscleDriver.name
    bpy.ops.object.mode_set(mode='POSE')




    #add constraint to bone tip

    tconstraint = obj.pose.bones[muscleTip].constraints.new('COPY_LOCATION')
    tconstraint.target = obj
    tconstraint.subtarget = muscleInsertion.name
    tconstraint.target_space = 'WORLD'
    tconstraint.owner_space = 'WORLD'


    # add constraints to muscle Offset

    oconstraint = obj.pose.bones[muscleOffset].constraints.new('COPY_LOCATION')
    oconstraint.target = obj
    oconstraint.subtarget = muscleTip
    oconstraint.target_space = 'LOCAL'
    oconstraint.owner_space = 'LOCAL'
    oconstraint.influence = 0.5
    oconstraint.use_offset = True

    # add stretch constraint to muscle Driver

    sconstraint =  obj.pose.bones[muscleDriver].constraints.new('STRETCH_TO')
    sconstraint.target = obj
    sconstraint.subtarget = muscleTip

    #add widgets to muscle  oirigin,insertion and offset
    bnf.add_widgetToBones([obj.pose.bones[muscleOffset], obj.pose.bones[muscleInsertion.name], obj.pose.bones[muscleOrigin.name]], wgt, (0.5,0.5,0.5))




class create_MuscleOperator(bpy.types.Operator):
    """creates  wavetail rig to control chain bones """
    bl_idname = "create.muscle"
    bl_label = "create muscle group"
    #class variables
    musclewgt: bpy.props.StringProperty()

    def execute(self, context):

        if bpy.context.active_bone:

            create_muscle(context.active_bone.name, context.object,self.musclewgt)
            self.report({'INFO'}, "generated successfurlly yarr!")
        else:

            self.report({'INFO'}, "something wrong matey?")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)
        pass

    def draw(self, context):
        layout = self.layout
        layout.label(text="create muscle group bones")
        layout = self.layout.row()
        layout.label(text="muscle group widget")
        layout.prop_search(self, "musclewgt", bpy.data, "objects", text="")

        pass







