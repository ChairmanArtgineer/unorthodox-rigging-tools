import bpy

def RemoveConsFunction():    
    for bone in bpy.context.selected_pose_bones:
        for c in bone.constraints:
            bone.constraints.remove(c) 

   
  
  
class RemoveConsOperator(bpy.types.Operator):
    """removes ALL Bone constrains... LOL"""
    bl_idname = "remove.all_constrains"
    bl_label = "dell bone constrains"
    
    def execute(self,context):
        RemoveConsFunction()
        
        return{'FINISHED'}
        
      
        
      




    
    


