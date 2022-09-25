bl_info = {
    "name": "unorthodox rigg tools",  # The name in the addon search menu
    "author": "chairman xi ",
    "description": "a addon for riggin with mixamo and other bizzarre toughts",
    "blender": (3, 2, 1),  # Lowest version to use
    "location": "View3D",
    "category": "Generic",
}
import bpy

from .mixamorenamer import RENAME_OT_Mtob
from .mixamorenamer import RENAME_OT_Btom
from .constains import RemoveConsOperator
from .parenting import ParentPoseMode



class VIEW3D_main_UI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "anti autodesk tools"
    bl_label = "very unorthodox rigg tools"
    bl_order = 0
    def draw(self, context):
        if (bpy.context.mode == 'POSE'):
            layout = self.layout

            row = layout.row()
            col = layout.column(align=True)
            row.label(text="constrains", translate=False)
            col.operator('remove.all_constrains',
                                 icon = 'CONSTRAINT_BONE')

            row = layout.row()
            col = layout.column(align=True)
            row.label(text="parenting", translate=False)
            col.operator('parent.posemode',
                                icon = 'BONE_DATA')
            col.prop(context.scene, 'ConnectBones')
            pass
class VIEW3D_MixamoUI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "anti autodesk tools"
    bl_label = "mixamo renamer"
    bl_order = 1

    def draw(self, context):
        if (bpy.context.mode == 'POSE'):
            self.layout.operator('rename.mixtoblend',
                                 icon = 'BLENDER')
            self.layout.operator('rename.blendtomix',
                                 icon = 'EVENT_M')
            pass


BlenderClasses = [
VIEW3D_main_UI,
VIEW3D_MixamoUI,
RENAME_OT_Mtob,
RENAME_OT_Btom,
RemoveConsOperator,
ParentPoseMode
]

def register():
    for blender_class in BlenderClasses:
        bpy.utils.register_class(blender_class)

def unregister():
    del bpy.types.Scene.ConnectBones
    for blender_class in BlenderClasses:
        bpy.utils.unregister_class(blender_class)

    print("hello world")



if __name__ == "__main__":
    register()


