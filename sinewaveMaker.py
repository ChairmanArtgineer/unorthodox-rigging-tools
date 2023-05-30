import bpy
from rigify.utils import mechanism as mecha
nbons = 20



def create_dupeBones(selection, prefix, newp):
    obj = bpy.context.active_object
    if obj.type == 'ARMATURE' and obj.mode == 'EDIT': 
          
        # if single bone append to list
        if isinstance(selection, bpy.types.EditBone):
            selectedBones = []
            selectedBones.append(selection)
        else:
            #equal list
            selectedBones = selection
            
        for bone in selectedBones:
            # create new bone with prefix
            new_bone_name = prefix + bone.name
            new_bone = obj.data.edit_bones.new(new_bone_name)
            #copy rest data from bone to new bone
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
            #select only the new chain
    

def find_Head(selection):
    for bone in selection:
        if bone.parent in selection:
            pass
        else:
            print("found end of the chain",bone.name)
            return bone   
    
    
    
    
                
   #start of the function      
#set tedit mode if not
def create_WaveTail(selection,dsp,sprl,freq):
    obj = bpy.context.active_object
    pbns = obj.pose.bones

    if (bpy.context.mode == "EDIT_ARMATURE"):
        pass
    else: 
       bpy.ops.object.mode_set(mode='EDIT')
        
    #subdivide bone chain
    endBone = find_Head(selection)
    create_dupeBones(endBone, "CTRL_", True)

    #go back to pose
    bpy.ops.object.mode_set(mode='POSE')
    print("mode set to",bpy.context.mode)

    #change references from edit to pose
    endBone = pbns[endBone.name]
    
     #extra bones for other functions
    dspBone = pbns[dsp]
    sprlBone = pbns[sprl]
    freqBone = pbns[freq]
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
        use_inherit_rotation = False
        
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
        
create_WaveTail(bpy.context.selected_editable_bones,"displace","spiral","shape N' Amp")
    
       
