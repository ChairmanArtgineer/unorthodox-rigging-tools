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




class VIEW3D_UI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "anti autodesk tools"
    bl_label = "very unorthodox rigg tools"
    bl_order = 0

    def draw(self, context):
        self.layout.operator('remove.all_constrains',
                             icon = 'CONSTRAINT_BONE')
        pass
class VIEW3D_UI2(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "anti autodesk tools"
    bl_label = "mixamo renamer"
    bl_order = 1

    def draw(self, context):
        self.layout.operator('rename.mixtoblend',
                             icon = 'BLENDER')
        self.layout.operator('rename.blendtomix',
                             icon = 'EVENT_M')
        pass


def register():
    bpy.utils.register_class(VIEW3D_UI)
    bpy.utils.register_class(VIEW3D_UI2)
    bpy.utils.register_class(RENAME_OT_Mtob)
    bpy.utils.register_class(RENAME_OT_Btom)
    bpy.utils.register_class(RemoveConsOperator)

    print("hello world")


def unregister():
    bpy.utils.unregister_class(VIEW3D_UI)
    bpy.utils.unregister_class(VIEW3D_UI2)
    bpy.utils.unregister_class(RENAME_OT_Mtob)
    bpy.utils.unregister_class(RENAME_OT_Btom)
    bpy.utils.unregister_class(RemoveConsOperator)

    print("hello world")

if __name__ == "__main__":
    register()


