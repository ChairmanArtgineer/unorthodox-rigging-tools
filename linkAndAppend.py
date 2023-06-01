import bpy
import pathlib

class get_WGTFromFile(bpy.types.Operator):
    """imports a widget collection from file """
    bl_idname = "get.wgt"
    bl_label = "get custom widgets "

    def execute(self, context):
        # check if we are running from the Text Editor
        if context.space_data != None and context.space_data.type == "TEXT_EDITOR":
            # get the path to the SAVED TO DISK script when running from blender
            print("bpy.context.space_data script_path")
            script_path = context.space_data.text.filepath
        else:
            print("__file__ script_path")
            # __file__ is built-in Python variable that represents the path to the script
            script_path = __file__

        print(f"script_path -> {script_path}")
        #get folder where script is in
        script_dir = pathlib.Path(script_path).resolve().parent
        print(f"[pathlib] script_dir -> {script_dir}")

        # get a path to a file that is next to the script
        path_to_file = str(script_dir / "WGTS.blend")
        print(f"path_to_file -> {path_to_file}")


        # Link the collection from the other file
        with bpy.data.libraries.load(path_to_file) as (data_from, data_to):
            data_to.collections = ["URT_WGTS"]

        # Append the linked collection to the current scene
        for collection in data_to.collections:
            context.collection.children.link(collection)
            collection.hide_viewport = True
            collection.hide_select = True
            collection.hide_render = True
        return {'FINISHED'}



