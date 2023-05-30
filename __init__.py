bl_info = {
    "name": "unorthodox rigg tools",  # The name in the addon search menu
    "author": "chairman xi ",
    "description": "a addon for riggin with mixamo and other bizzarre toughts",
    "blender": (3, 0, 0),  # Lowest version to use
    "location": "View3D",
    "category": "Rigging",
}
import bpy


from . import constains
from . import mixamorenamer



class VIEW3D_main_UI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "anti autodesk tools"
    bl_label = "very unorthodox rigg tools"
    bl_idname = "MAIN_UI"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return context.object.mode == 'POSE'
    def draw(self, context):
            pass





BlenderClasses = [
VIEW3D_main_UI
]

def register():
    for blender_class in BlenderClasses:
        bpy.utils.register_class(blender_class)
    constains.register()
    mixamorenamer.register()

def unregister():
    for blender_class in BlenderClasses:
        bpy.utils.unregister_class(blender_class)
    constains.unregister()
    mixamorenamer.unregister()
    print("hello world")



if __name__ == "__main__":
        register()

