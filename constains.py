import bpy
from . import boneFunctions as bnf

class constraints_Props(bpy.types.PropertyGroup):
    cname : bpy.props.StringProperty(
        name="cname",
        default="",
        )
def remove_AllCons(selection):
    for bone in selection:
        for c in bone.constraints:
            bone.constraints.remove(c) 
def remove_ConByName(selection,cname):
    for bone in selection:
        for c in bone.constraints:
            if cname == c.name:
                bone.constraints.remove(c)
            else:
                pass


class remove_c_name(bpy.types.Operator):
    """ removes contrains by name"""
    bl_idname = "removec.name"
    bl_label = "remove cons by name"


    def execute(self, context):
        remove_ConByName(bpy.context.selected_pose_bones, context.scene.constraintProps.cname)

        return {'FINISHED'}
  
  
class RemoveCons_Operator(bpy.types.Operator):
    """removes ALL Bone constrains... LOL"""
    bl_idname = "remove.all_constrains"
    bl_label = "dell bone constrains"

    def execute(self,context):
        remove_AllCons(bpy.context.selected_pose_bones)
        
        return{'FINISHED'}
        
class select_byC(bpy.types.Operator):
    """ selects bones by constaint name"""
    bl_idname = "select.byc"
    bl_label = "select bone by constraint"



    def execute(self, context):

        bnf.select_ByConstraint(bpy.context.selected_pose_bones,context.scene.constraintProps.cname)
        return {'FINISHED'}


class VIEW3D_constraint_UI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "MAIN_UI"
    bl_category = "anti autodesk tools"
    bl_label = "constraint related"
   # bl_options = {'HIDE_HEADER'}
    @classmethod
    def poll(cls, context):
        if bpy.context.object:
            return context.object.mode == 'POSE'
    def draw(self, context):
        if (bpy.context.mode == 'POSE'):

            layout = self.layout

            row = layout.row()
            col = layout.column()
            #row.label(text="constrains", translate=False)
            col.operator('remove.all_constrains',
                         icon='CONSTRAINT_BONE')
            col.separator()
            col.operator('removec.name',
                         icon='CONSTRAINT_BONE')
            col.operator('select.byc',
                         icon='CONSTRAINT_BONE')
            #col.prop(context.scene.constraintProps,'cname')
            col.prop_search(context.scene.constraintProps, "cname", context.active_pose_bone, "constraints", text="")




            col.separator()
            row = layout.row()
            col = layout.column(align=True)
            pass

BlenderClasses = [
VIEW3D_constraint_UI,
select_byC,
RemoveCons_Operator,
remove_c_name,
constraints_Props
]
def register():
    for blender_class in BlenderClasses:
        bpy.utils.register_class(blender_class)
    bpy.types.Scene.constraintProps = bpy.props.PointerProperty(
        type=constraints_Props)



def unregister():
    del bpy.types.Scene.constraintProps
    for blender_class in BlenderClasses:
        bpy.utils.unregister_class(blender_class)







    
    


