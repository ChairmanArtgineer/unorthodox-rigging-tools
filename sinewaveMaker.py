import bpy
from rigify.utils import mechanism as mecha
from . import boneFunctions as bnf

def create_WaveTail(obj,selection,dsp,sprl,freq):
    pbns = obj.pose.bones

    if (bpy.context.mode == "EDIT_ARMATURE"):
        pass
    else: 
       bpy.ops.object.mode_set(mode='EDIT')
        
    #find head and create ctrl bone
    endBone = bnf.find_Head(selection)
    bnf.create_dupeBones(obj,endBone, "CTRL_", True)

    #set rotation mode
    for bone in bpy.context.selected_editable_bones:
        bone.use_inherit_rotation = False

    #go back to pose
    bpy.ops.object.mode_set(mode='POSE')
    print("mode set to",bpy.context.mode)

    #change references from edit to pose
    endBone = pbns[endBone.name]
    
     #extra bones for other functions
    dspBone = pbns[dsp]
    dspBone.rotation_mode = 'XYZ'
    sprlBone = pbns[sprl]
    sprlBone.rotation_mode = 'XYZ'
    freqBone = pbns[freq]
    freqBone.rotation_mode = 'XYZ'
    print("extrabones added")
    
    #create custom properties for the end bone and ad its driver
    
    #add main fac driver MUST DO THIS
    mecha.make_property(endBone, name = "fac", default = 0.0, min=-1e6, max=1e6,overridable=True)
    d = endBone.driver_add('["fac"]')
    d.driver.type = 'AVERAGE'
    varr = d.driver.variables.new()
    varr.name = "y_rot"
    varr.targets[0].id = obj
    varr.targets[0].data_path = sprlBone.path_from_id('rotation_euler') + "[1]"
    d.update()
    mecha.make_property(endBone, name = "amp", default = 0.0, min=-2, max=2,overridable=True)
    mecha.make_property(endBone, name = "c_amp", default = 0.0, min=-2, max=2,overridable=True) 
    mecha.make_property(endBone, name = "freq", default = 0.0, min=-5, max=5,overridable=True)
    mecha.make_property(endBone, name = "offset", default = 0.0, min=-5, max=5,overridable=True)
    print("properties added to:", endBone.name)
    

    

    #set driver for each bone in the chain
    c_ind = 1

    for bone in bpy.context.selected_pose_bones:
        #set parenting relations

        
        #find lenght of the chain
        l = len(bpy.context.selected_pose_bones)
        
        bone.rotation_mode = 'XYZ'
        #driver on X
        d = bone.driver_add('rotation_euler', 0) 
        d.driver.expression =  "sin((fac  -  " + str(c_ind) + " - off"+ ")*freq" + ")/"+ str(round(l/c_ind,2) )  + " * amp  " 
        
        #create amp variable
        var = d.driver.variables.new()
        var.name = "amp"
        var.targets[0].id = obj
        var.targets[0].data_path = endBone.path_from_id('["amp"]') 
        
        #create wave freq variable
        var = d.driver.variables.new()
        var.name = "freq"
        var.targets[0].id = obj
        var.targets[0].data_path = endBone.path_from_id('["freq"]')
        
        #create displace factor variable
        var = d.driver.variables.new()
        var.name = "fac"
        var.targets[0].id = obj
        var.targets[0].data_path = endBone.path_from_id('["fac"]')
        var = d.driver.variables.new()
        
        #create offset variable
        var.name = "off"
        var.targets[0].id = obj
        var.targets[0].data_path = endBone.path_from_id('["offset"]')
        #update the driver
        d.update()
        
        
        #driver on z
        d = bone.driver_add('rotation_euler', 2) 
        d.driver.expression =  "cos((fac   - " + str(c_ind)  + "- off"+ ")*freq" + ")/ "+ str(round(l/c_ind,2) )   + " * (amp * c_amp) " 
        #create amp variable
        var = d.driver.variables.new()
        var.name = "amp"
        var.targets[0].id = obj
        var.targets[0].data_path = endBone.path_from_id('["amp"]')
         
        var = d.driver.variables.new()
        var.name = "c_amp"
        var.targets[0].id = obj
        var.targets[0].data_path = endBone.path_from_id('["c_amp"]') 
        
        
        var = d.driver.variables.new()
        var.name = "freq"
        var.targets[0].id = obj
        var.targets[0].data_path = endBone.path_from_id('["freq"]')
        
        var = d.driver.variables.new()
        var.name = "off"
        var.targets[0].id = obj
        var.targets[0].data_path = endBone.path_from_id('["offset"]')
        
        var = d.driver.variables.new()
        var.name = "fac"
        var.targets[0].id = obj
        var.targets[0].data_path = endBone.path_from_id('["fac"]')
        #update the driver
        d.update()  
        
        #displace constraint with influence curve
        constraint = bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = "Displace"
        constraint.target = obj
        constraint.subtarget = dspBone.name
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        constraint.mix_mode = 'BEFORE_FULL'
        constraint.influence = round(((1/l)*(c_ind-1))**2,2)
        if constraint.influence == 0:
            bone.constraints.remove(constraint)
        
        constraint = bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = "Tail_Parent"
        constraint.target = obj
        constraint.subtarget = "CTRL_" + endBone.name
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        constraint.mix_mode = 'BEFORE_FULL'
        constraint.influence = 1.0
        
       
        print("success on: ",bone.name,"index",c_ind)
        c_ind += 1
    
    print("ajoy matey, generation successfully")
        
#create_WaveTail(bpy.context.selected_editable_bones,"displace","spiral","shape N' Amp")

class create_WaveTailOperator(bpy.types.Operator):

    bl_idname = "create.wavetail"
    bl_label = "create sine-wave tail"

    dsp_bone: bpy.props.StringProperty()
    sprl_bone: bpy.props.StringProperty()
    freq_bone: bpy.props.StringProperty()


    def execute(self, context):
        #obj = bpy.context.active_object

        if self.dsp_bone and self.sprl_bone and self.freq_bone:
            create_WaveTail(context.object, bpy.context.selected_editable_bones, self.dsp_bone, self.sprl_bone,self.freq_bone)
            self.report({'INFO'}, "generated successfurlly yarr!" )
        else:
            self.report({'INFO'}, "something wrong matey?")

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Select a bone:")
        layout.prop_search(self, "dsp_bone", context.object.data, "bones", text="displace bone")
        layout.prop_search(self, "sprl_bone", context.object.data, "bones", text="spiral bone")
        layout.prop_search(self, "freq_bone", context.object.data, "bones", text="freq bone")

class VIEW3D_WaveTail_UI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "MAIN_UI"
    bl_category = "anti autodesk tools"
    bl_label = "shelf related"
   # bl_options = {'HIDE_HEADER'}
    @classmethod
    def poll(cls, context):
        return context.object.mode == 'EDIT'
    def draw(self, context):


        layout = self.layout
        col = layout.column()
        col.operator('create.wavetail',
                     icon='CONSTRAINT_BONE')

        col.separator()
        row = layout.row()
        col = layout.column(align=True)
        pass
BlenderClasses = [
VIEW3D_WaveTail_UI,
create_WaveTailOperator
]

def register():
    for blender_class in BlenderClasses:
        bpy.utils.register_class(blender_class)

def unregister():

    for blender_class in BlenderClasses:
        bpy.utils.unregister_class(blender_class)

