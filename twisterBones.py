import bpy


def create_Twister(cuts, drv, og, inverse=False):
    # driverBone = bpy.context.selected_bones[1].name
    # ogBone = bpy.context.active_bone.name
    driverBone = drv
    ogBone = og
    # create some refs

    Pbones = bpy.context.active_object.pose.bones
    Ebones = bpy.context.active_object.data.edit_bones

    # duplicate the og bone with Twist prefix
    bpy.ops.armature.bone_primitive_add(name="TWST_" + ogBone)
    twistBone = Ebones["TWST_" + ogBone]
    twistBone.head = Ebones[ogBone].head
    twistBone.tail = Ebones[ogBone].tail
    twistBone.roll = Ebones[ogBone].roll

    # parent new bone to the og bone

    twistBone.parent = Ebones[ogBone]

    # subdivide the new bone a
    twistBone.select = True
    bpy.ops.armature.subdivide(number_cuts=cuts)

    # get the new bones names

    #twstBones = bpy.context.selected_bones

    # switch to pose mode

    bpy.ops.object.mode_set(mode='POSE')

    # set rotation modes to euler

    Pbones[driverBone].rotation_mode = 'XYZ'
    Pbones[ogBone].rotation_mode = 'XYZ'

    for bone in bpy.context.selected_pose_bones:

        bone.rotation_mode = 'XYZ'

        # number of bones
        l = len(bpy.context.selected_pose_bones)
        # create driver on bone
        d = bone.driver_add('rotation_euler', 1)
        # create twist variable
        var = d.driver.variables.new()
        var.name = "twist"
        var.targets[0].id = bpy.context.active_object
        var.targets[0].data_path = Pbones[driverBone].path_from_id('rotation_euler') + "[1]"

        if inverse and bone.name == "TWST_" + ogBone:
            d.driver.expression = "twist/" + str((l + 1) * 2) + "-twist"

        else:
            d.driver.expression = "twist / " + str(l + 1)

        # print a finish or smt idk


class create_TwisterOperator(bpy.types.Operator):
    """creates  wavetail rig to control chain bones """
    bl_idname = "create.twister"
    bl_label = "create twister bones"

    n_cuts: bpy.props.IntProperty(default=1)
    inv: bpy.props.BoolProperty(default=False)

    def execute(self, context):

        if self.n_cuts and context.active_bone:
            if self.inv:
                create_Twister(self.n_cuts, context.active_bone.name, context.active_bone.name, True)
                self.report({'INFO'}, "generated successfurlly yarr!")
            elif context.selected_bones and len(context.selected_bones) == 2:
                create_Twister(self.n_cuts, context.selected_bones[1].name, context.active_bone.name)
                self.report({'INFO'}, "generated successfurlly yarr!")

        else:

            self.report({'INFO'}, "something wrong matey?")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def draw(self, context):
        layout = self.layout
        layout.label(text="number of cuts:")
        layout.prop(self, 'n_cuts', text="")
        layout.prop(self, 'inv', text="use inverse")

