import bpy
from rigify.utils import mechanism as mecha
import mathutils
from . import boneFunctions as bnf
from . import sinewaveMaker as swm
from . import linkAndAppend as lna
from . import twisterBones as twst
from . import muscleGroup as msc
from . import ribbons as rbb


def create_IkFk(obj,selection,fkPrefix,ikPrefix,fkWgt=None,ikWgt=None,poleWgt=None):

    #create fk chain
    fk_chain = bnf.create_dupeBones(obj, selection, fkPrefix, True)
    ik_chain = bnf.create_dupeBones(obj, selection, ikPrefix, True)

    # update refernces
    obj.update_from_editmode()
    ikNames = bnf.find_BonesByName(obj, ik_chain, "POSE")

    ik_chain = bnf.find_BonesByName(obj, ik_chain, "EDIT")
    fk_chain = bnf.find_BonesByName(obj, fk_chain, "POSE")


    #set widgets
    ikpole = bnf.add_IK(obj, ik_chain,ikWgt,poleWgt)

    bnf.add_widgetToBones(fk_chain,fkWgt,(1/2,1/2,1/2))





    # update shit this  function is so good





    #set drivers in widget scales

    #create custom prop on the end bone 
    target = bnf.find_Tail(bpy.context.selected_pose_bones)


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

    # set drivers for fk widdigets
    for bone in fk_chain:
        for axis in range(3):
            ogscle = bone.custom_shape_scale_xyz[axis]
            d = bone.driver_add('custom_shape_scale_xyz', axis)
            d.driver.expression = "var * " + str(ogscle)

            var = d.driver.variables.new()
            var.name = "var"
            var.targets[0].id = obj
            var.targets[0].data_path = target.path_from_id('["Follow"]')
        # set drivers for fk widdigets

    #set drivers for the ik widgets
    for bone in ikNames:
        for axis in range(3):
            ogscle = bone.custom_shape_scale_xyz[axis]
            d = bone.driver_add('custom_shape_scale_xyz', axis)
            d.driver.expression = "(1-var) * " + str(ogscle)

            var = d.driver.variables.new()
            var.name = "var"
            var.targets[0].id = obj
            var.targets[0].data_path = target.path_from_id('["Follow"]')
    #add driver to ik pole

    for axis in range(3):
        d = ikpole.driver_add('custom_shape_scale_xyz', axis)
        d.driver.expression = "(1-var) * " + str(ogscle)
        var = d.driver.variables.new()
        var.name = "var"
        var.targets[0].id = obj
        var.targets[0].data_path = target.path_from_id('["Follow"]')
    
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
        var.targets[0].data_path = target.path_from_id() + '["' + p_name + '"]'
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
        var.targets[0].data_path = target.path_from_id() + '["' + p_name + '"]'
        follow_d.update()
    

        
class create_Ctrl(bpy.types.Operator):
    """creates control bones for the selected bones """
    bl_idname = "create.ctrl"
    bl_label = "create ctrl chain "

    prefix: bpy.props.StringProperty()
    wgt: bpy.props.StringProperty()
    space: bpy.props.EnumProperty(
        items=[('WORLD', 'world space', ''),
               ('LOCAL', 'local space', '')],
        default= 'WORLD'
    )
    type: bpy.props.EnumProperty(
        items=[('CHILD_OF', 'Child Of ', ''),
               ('COPY_TRANSFORMS', 'Copy Transforms', '')],
        default='COPY_TRANSFORMS'
    )

    def execute(self, context):

        if self.prefix:
            fkchain = bnf.create_dupeBones(context.object,context.selected_bones,self.prefix)
            bpy.ops.object.mode_set(mode = 'POSE')
            bnf.add_follow(context.object,context.selected_pose_bones,self.prefix,self.space, self.type)
            fkchain = bnf.find_BonesByName(context.object,fkchain,"POSE")
            bnf.add_widgetToBones(fkchain,self.wgt)
            self.report({'INFO'}, "generated successfurlly yarr!")
        else:
            self.report({'INFO'}, "something wrong matey?")

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.label(text= "I hope you selected at least 1 bone...")

        layout = self.layout.row()
        layout.label(text="prefix ")
        layout.prop(self, 'prefix', text="")

        layout = self.layout.row()
        layout.label(text="constraint type")
        layout.prop(self, 'type', text="")
        if self.type == 'COPY_TRANSFORMS':
            layout = self.layout.row()
            layout.label(text="ctrl space")
            layout.prop(self, 'space', text="")

        layout = self.layout.row()
        layout.label(text="widget for all")
        layout.prop_search(self, "wgt", bpy.data, "objects", text="")



class create_IkFkOperator(bpy.types.Operator):
    """ creates an ik and fk chain with a follow property """
    bl_idname = "create.ikfk"
    bl_label = "create ik and fk chains"
    ikWgt: bpy.props.StringProperty()
    fkWgt: bpy.props.StringProperty()
    poleWgt: bpy.props.StringProperty()
    ikPrefix: bpy.props.StringProperty(default= "IK_")
    fkPrefix: bpy.props.StringProperty(default= "FK_")


    def execute(self, context):

        if self.ikPrefix and self.fkPrefix:
            create_IkFk(context.object, context.selected_bones, self.fkPrefix, self.ikPrefix,self.fkWgt,self.ikWgt,self.poleWgt)
            self.report({'INFO'}, "generated successfurlly yarr!")
        else:
            self.report({'INFO'}, "something wrong matey?")

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200)

    def draw(self, context):

        layout = self.layout
        layout.label(text="only works ith 3 bones")
        layout.label(text="set prefixes:")
        layout = self.layout.row()
        layout.label(text="ik prefix")
        layout.prop(self, 'ikPrefix', text="")
        layout = self.layout.row()
        layout.label(text="fk prefix")
        layout.prop(self, 'fkPrefix', text="")
        layout = self.layout.row()
        layout.label(text="widget fk chain")
        layout.prop_search(self, "fkWgt", bpy.data, "objects", text="")
        layout = self.layout.row()
        layout.label(text="widget  ik target")
        layout.prop_search(self, "ikWgt", bpy.data, "objects", text="")
        layout = self.layout.row()
        layout.label(text="widget  pole bone")
        layout.prop_search(self, "poleWgt", bpy.data, "objects", text="")

class add_IkOperator(bpy.types.Operator):
    """ adds ik system to the current selected bones and spawns pole bone """
    bl_idname = "add.ik"
    bl_label = "add ik for 3 selected bones"


    def execute(self, context):

        if len(context.selected_bones) == 3:
            bnf.add_IK(context.object, context.selected_bones)
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
        if context.object:
            return context.object.mode == 'EDIT'
    def draw(self, context):


        layout = self.layout
        if 'URT_WGTS' not in bpy.data.collections:
            layout = self.layout.column()
            layout.operator('get.wgt',
                         icon='OUTLINER_COLLECTION')

        col = self.layout.column()
        col.label(text = "custom rigs")
        col.operator('create.wavetail',
                     icon='FORCE_HARMONIC')
        col.operator('create.muscle', icon= 'META_ELLIPSOID')


        col = self.layout.column()
        col.label(text="build blocks")
        col.operator('create.ikfk',
                     icon='GP_MULTIFRAME_EDITING')
        col.operator('create.ctrl',icon='GP_MULTIFRAME_EDITING')
        col.operator('add.ik',icon='CON_KINEMATIC')
        col.operator('create.twister', icon='MOD_SCREW')
        col.operator('create.ribbon', icon='OUTLINER_OB_GREASEPENCIL')


        col.separator()
        row = layout.row()
        col = layout.column(align=True)
        pass

BlenderClasses =[

VIEW3D_SimpleGen_UI,
create_IkFkOperator,
add_IkOperator,
create_Ctrl,
swm.create_WaveTailOperator,
lna.get_WGTFromFile,
twst.create_TwisterOperator,
msc.create_MuscleOperator,
rbb.create_RibbonOperator
]

def register():
    for blender_class in BlenderClasses:
        bpy.utils.register_class(blender_class)



def unregister():
    for blender_class in BlenderClasses:
        bpy.utils.unregister_class(blender_class)



           
            
       
