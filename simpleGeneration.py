import bpy
from rigify.utils import mechanism as mecha
import mathutils
from . import boneFunctions as bnf
from . import sinewaveMaker as swm







def add_IK(obj,selection):
    """creates an ik chain from 3 bones and adds a pole bone"""
    pbone = obj.pose.bones
    
         
    ikTarget = bnf.find_Tail(selection)
    ikBone = ikTarget.parent
    ikEnd = ikBone.parent
    
    #clear parent for ik target
    ikTarget.parent = None
    
    #get a position for the pole bone 
    barycenter = (ikTarget.head + ikBone.head + ikEnd.head)/3 
    fkPole = ( ikBone.head - barycenter) * 4
    fkPole =   mathutils.Matrix.Translation(fkPole) @ (ikBone.matrix) 
    
        
    #place pole bone
    ikPole = obj.data.edit_bones.new( ikEnd.name + "_Pole")
    ikPole.head = (0,0,0)
    ikPole.tail = (0,0,1)
    ikPole.matrix = fkPole
    ikPole.tail = ikPole.head + mathutils.Vector((0,0,1))
    print("pole vector generated:", ikPole.name)
    

    #calculate pole angle
    #def get_pole_angle(base_bone, ik_bone, pole_location):
    pole_normal = (ikBone.tail - ikEnd.head).cross(ikPole.matrix.translation - ikEnd.head)
    projected_pole_axis = pole_normal.cross(ikEnd.tail - ikEnd.head)
    poleAngle = ikEnd.x_axis.angle(projected_pole_axis)
    
    if ikEnd.x_axis.cross(projected_pole_axis).angle(ikEnd.tail-ikEnd.head) < 1:
        poleAngle = -poleAngle
    #poleAngle = (180 * poleAngle) // 3.14159265359 
    print("pole angle generated:",(180 * poleAngle) // 3.14159265359)
    
    
    #set the pole bone to its name for later use
    ikPole = ikPole.name
    ikTarget = ikTarget.name
    ikEnd = ikEnd.name
    ikBone = ikBone.name  
    
    #set pose mode
    
    bpy.ops.object.mode_set(mode='POSE')
    
    
    #copy transforms for the ik bones
    
    #get the dupebones from names to pose bones         //objref
    
    #reset ik references
    ikBone = pbone[ikBone]
    ikEnd = pbone[ikEnd]
    ikTarget = pbone[ikTarget]
    ikPole = pbone[ikPole]         
    
    #create ik constraint
    constraint = ikBone.constraints.new('IK')
    constraint.target = obj
    constraint.subtarget = ikTarget.name
    constraint.pole_target = obj
    constraint.pole_subtarget = ikPole.name  
    constraint.chain_count = 2
    constraint.pole_angle = poleAngle
    

           
def create_IkFk(obj,selection,fkPrefix,ikPrefix):
    pbone = obj.pose.bones
    #create fk chain
    bnf.create_dupeBones(obj,selection, fkPrefix, True)
    
    #call the function inptus :selected and active bone 
    #create ik bones dictionary
    ikTarget = bnf.find_Tail(selection)
    ikBone = ikTarget.parent
    ikEnd = ikBone.parent
    #create ik chain
    bnf.create_dupeBones(obj,selection, ikPrefix, True)
    

    #clear the parent from ik target
    
    bpy.context.active_object.data.edit_bones[ikPrefix + ikTarget.name].parent = None

    #get a position for the pole bone 
    barycenter = (ikTarget.head + ikBone.head + ikEnd.head)/3 
    fkPole = ( ikBone.head - barycenter) * 4
    fkPole =   mathutils.Matrix.Translation(fkPole) @ (ikBone.matrix) 
    
        
    #place pole bone
    ikPole = obj.data.edit_bones.new(ikPrefix + ikEnd.name + "_Pole")
    ikPole.head = (0,0,0)
    ikPole.tail = (0,0,1)
    ikPole.matrix = fkPole
    ikPole.tail = ikPole.head + mathutils.Vector((0,0,1))
    print("pole vector generated:", ikPole.name)
    

    ##TODO make the whole pole thing a single function ffs
    #calculate pole angle
    #def get_pole_angle(base_bone, ik_bone, pole_location):
    pole_normal = (ikBone.tail - ikEnd.head).cross(ikPole.matrix.translation - ikEnd.head)
    projected_pole_axis = pole_normal.cross(ikEnd.tail - ikEnd.head)
    poleAngle = ikEnd.x_axis.angle(projected_pole_axis)
    if ikEnd.x_axis.cross(projected_pole_axis).angle(ikEnd.tail-ikEnd.head) < 1:
        poleAngle = -poleAngle
    #poleAngle = (180 * poleAngle) // 3.14159265359 
    print("pole angle generated:",(180 * poleAngle) // 3.14159265359)
    
    
    #set the pole bone to its name for later use
    ikPole = ikPole.name
    
    #set mode to pose
    bpy.ops.object.mode_set(mode='POSE')
    
    #reset target bone reference
    ikTarget = pbone[ikTarget.name]
    
    #create custom prop on the end bone 
    target = ikTarget
    p_name = "Follow"
    follow_p = mecha.make_property(target,
    name = p_name, 
    default = 0.0, 
    min=0, 
    max=1, 
    soft_min=None, 
    soft_max=None, 
    description=None, 
    overridable=True)
    #////
    
    follow_p = 1.0
    
    #apply driver to each bone
    for bone in bpy.context.selected_pose_bones: 
        #create fk follow
        constraint = bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = fkPrefix + p_name
        constraint.target = obj
        constraint.subtarget = fkPrefix + bone.name
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'
        
        #create fk follow driver
        follow_d = constraint.driver_add('influence')
        follow_d.driver.type = "SCRIPTED"
        follow_d.driver.expression = 'var'
        var = follow_d.driver.variables.new()
        var.targets[0].id = obj
        var.targets[0].data_path = ikTarget.path_from_id() + '["' + p_name + '"]'
        follow_d.update()
        
        #create ik follow
        
        constraint = bone.constraints.new('COPY_TRANSFORMS')
        constraint.name = ikPrefix + p_name
        constraint.target = obj
        constraint.subtarget =  ikPrefix + bone.name
        constraint.target_space = 'WORLD'
        constraint.owner_space = 'WORLD'
        
        #create ik follow driver
        
        follow_d = constraint.driver_add('influence')
        follow_d.driver.type = "SCRIPTED"
        follow_d.driver.expression = '1 - var'
        var = follow_d.driver.variables.new()
        var.targets[0].id = obj
        var.targets[0].data_path = ikTarget.path_from_id() + '["' + p_name + '"]'
        follow_d.update()
    
    #reset ik references
    #ignore the error python just cant read shit
    ikBone = pbone[ikPrefix + ikBone.name]
    ikTarget = pbone[ikPrefix + ikTarget.name]
    ikPole = pbone[ikPole]         
    
    #create ik constraint
    constraint = ikBone.constraints.new('IK')
    constraint.target = obj
    constraint.subtarget = ikTarget.name
    constraint.pole_target = obj
    constraint.pole_subtarget = ikPole.name  
    constraint.chain_count = 2
    constraint.pole_angle = poleAngle
        
class create_Ctrl(bpy.types.Operator):
    """creates control bones for the selected bones """
    bl_idname = "create.ctrl"
    bl_label = "create ctrl chain "

    prefix: bpy.props.StringProperty()
    useParent: bpy.props.BoolProperty()
    space: bpy.props.EnumProperty(
        items=[('WORLD', 'world space', ''),
               ('LOCAL', 'local space', '')],
        default= 'WORLD'
    )

    def execute(self, context):

        if self.prefix and self.useParent:
            bnf.create_dupeBones(context.object,context.selected_bones,self.prefix,self.useParent)
            bpy.ops.object.mode_set(mode = 'POSE')
            bnf.add_follow(context.object,context.selected_pose_bones,self.prefix,self.space)
            self.report({'INFO'}, "generated successfurlly yarr!")
        else:
            self.report({'INFO'}, "something wrong matey?")

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text= "I hope you selected at least 1 bone...")
        layout.prop(self, 'prefix', text="prefix for ctrl bones")
        layout.prop(self, 'space', text="ctrl space")
        layout.prop(self, 'useParent', text="use new parent")

class create_IkFkOperator(bpy.types.Operator):
    """ creates an ik and fk chain with a follow property """
    bl_idname = "create.ikfk"
    bl_label = "create ik and fk chains"

    ikPrefix: bpy.props.StringProperty()
    fkPrefix: bpy.props.StringProperty()


    def execute(self, context):

        if self.ikPrefix and self.fkPrefix:
            create_IkFk(context.object, context.selected_bones, self.fkPrefix, self.ikPrefix)
            self.report({'INFO'}, "generated successfurlly yarr!")
        else:
            self.report({'INFO'}, "something wrong matey?")

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.label(text="I hope you selected only 3 chain  bones...")
        layout.label(text="set prefixes")
        layout.prop(self, 'ikPrefix', text="ik prefix")
        layout.prop(self, 'fkPrefix', text="fk prefix")

class add_IkOperator(bpy.types.Operator):
    """ adds ik system to the current selected bones and spawns pole bone """
    bl_idname = "add.ik"
    bl_label = "add ik for 3 selected bones"


    def execute(self, context):

        if len(context.selected_bones) == 3:
            add_IK(context.object, context.selected_bones)
            self.report({'INFO'}, "generated successfurlly yarr!")

        else:
            self.report({'INFO'}, "something wrong matey?")

        return {'FINISHED'}

class VIEW3D_SimpleGen_UI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "MAIN_UI"
    bl_category = "anti autodesk tools"
    bl_label = "shelf related"
    #bl_options = {'HIDE_HEADER'}
    @classmethod
    def poll(cls, context):
        return context.object.mode == 'EDIT'
    def draw(self, context):


        layout = self.layout
        col = layout.column()
        col.label(text = "custom rigs")
        col.operator('create.wavetail',
                     icon='FORCE_HARMONIC')
        layout = layout.row()
        col = layout.column()
        col.label(text="build blocks")
        col.operator('create.ikfk',
                     icon='GP_MULTIFRAME_EDITING')
        col.operator('create.ctrl',icon='GP_MULTIFRAME_EDITING')
        col.operator('add.ik',icon='CON_KINEMATIC')


        col.separator()
        row = layout.row()
        col = layout.column(align=True)
        pass

BlenderClasses =[
VIEW3D_SimpleGen_UI,
create_IkFkOperator,
add_IkOperator,
create_Ctrl,
swm.create_WaveTailOperator
]

def register():
    for blender_class in BlenderClasses:
        bpy.utils.register_class(blender_class)




def unregister():
    for blender_class in BlenderClasses:
        bpy.utils.unregister_class(blender_class)



           
            
       
