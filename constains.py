import bpy
from . import boneFunctions as bnf

class constraints_Props(bpy.types.PropertyGroup):
    """ store global like variables """
    cname : bpy.props.StringProperty(
        name="cname",
        default="",
        )
    cindex : bpy.props.IntProperty(name='cindex', default=0)
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

def move_constraint(selection, targetC, newIndex):
    """
    moves constraint in the stack  based on index
    :param selection: list of pose bones
    :param targetC: name of the desired constraint
    :param newIndex: new position starting from 0
    """
    for bone in selection:
        #get lenght of constriants
        l = len(bone.constraints)
        for i, c in enumerate(bone.constraints):
            if c.name == targetC:
                #move constraints and fix if new index is out of range
                if newIndex < l:
                    bone.constraints.move(min(i,l-1),max(0,newIndex))
                else:
                    bone.constraints.move(min(i,l-1),l -1)
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

class Move_ConstraintOpearator(bpy.types.Operator):
    """moves the constraint position in the stack """
    bl_idname = "move.constraint"
    bl_label = "move constraint"

    def execute(self, context):
        move_constraint(context.selected_pose_bones, context.scene.constraintProps.cname, context.scene.constraintProps.cindex)

        return {'FINISHED'}
class Reset_ChildInverseOperator(bpy.types.Operator):
    """ resets the inverse in a child of constraint"""
    bl_idname = "reset.childof"
    bl_label = "reset childOf inverse"

    def execute(self, context):
        bnf.set_childofInverse(context.object,context.selected_pose_bones, context.scene.constraintProps.cname)

        return {'FINISHED'}

class VIEW3D_constraint_UI(bpy.types.Panel):
    bl_idname = "CONSTRAINT_PT_UI"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "MAIN_PT_UI"
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
            col.prop(context.scene.constraintProps,'cname')
            col.label(text = "constraint especific")
            col.prop(context.scene.constraintProps,'cindex')
            col.operator('reset.childof',
             icon='CON_CHILDOF')
            col.operator('move.constraint', icon ='CONSTRAINT_BONE')


            #col.prop_search(context.scene.constraintProps, "cname", context.active_pose_bone, "constraints", text="")



            col.separator()
            row = layout.row()
            col = layout.column(align=True)
            pass

BlenderClasses = [
VIEW3D_constraint_UI,
select_byC,
RemoveCons_Operator,
remove_c_name,
constraints_Props,
Reset_ChildInverseOperator,
Move_ConstraintOpearator
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







    
    


