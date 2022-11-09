import bpy

def RemoveConsFunction():    
    for bone in bpy.context.selected_pose_bones:
        for c in bone.constraints:
            bone.constraints.remove(c) 
def remove_c_name_fnc(input):
    for bone in bpy.context.selected_pose_bones:
        for c in bone.constraints:
            if input == c.name:
                bone.constraints.remove(c)
            else:
                pass

def select_byc_fnc(Input):
    for bone in bpy.context.selected_pose_bones:
        print(len(bone.constraints))
        if (len(bone.constraints) > 0):
            for c in bone.constraints:
                if Input == c.name:
                    bone.bone.select = True
                else:
                    bone.bone.select = False
        else:
            bone.bone.select = False
class remove_c_name(bpy.types.Operator):
    """ removes contrains by name"""
    bl_idname = "removec.name"
    bl_label = "remove cons by name"

    bpy.types.Scene.Cons_name = bpy.props.StringProperty(
        name='constrain name',default="")
    def execute(self, context):
        remove_c_name_fnc(context.scene.Cons_name)

        return {'FINISHED'}
  
  
class RemoveConsOperator(bpy.types.Operator):
    """removes ALL Bone constrains... LOL"""
    bl_idname = "remove.all_constrains"
    bl_label = "dell bone constrains"
    
    def execute(self,context):
        RemoveConsFunction()
        
        return{'FINISHED'}
        
class select_byC(bpy.types.Operator):
    """ selects bones by constaint name"""
    bl_idname = "select.byc"
    bl_label = "select bone by constraint"
    def execute(self, context):
        select_byc_fnc(context.scene.Cons_name)
        return {'FINISHED'}
        
      




    
    


