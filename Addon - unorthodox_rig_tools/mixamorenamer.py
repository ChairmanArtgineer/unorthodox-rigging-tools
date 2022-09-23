import bpy


def Mixamo_TO_Blender_Rename(bonename, side, suffix):
    if ("mixamorig:" in bonename):
        head, tails = bonename.split(':')
        if (head == "mixamorig"):
            tails = tails[(len(side)):]
            bonename = tails + suffix
        else:
            tails = tails[-(len(side)):]
            bonename = tails
    return bonename
    print(bonename)


def Blender_TO_Mixamo_Rename(bonename, prefix):
    bonename = bonename[:-2]
    bonename = "mixamorig:" + prefix + bonename
    return bonename


def Blender_TO_Mixamo_Fnc(MixBones):
    if (".R" in MixBones):
        MixBones = Blender_TO_Mixamo_Rename(MixBones, "Right")
    if (".L" in MixBones):
        MixBones = Blender_TO_Mixamo_Rename(MixBones, "Left")
    else:
        if ("mixamorig:" not in MixBones):
            MixBones = "mixamorig:" + MixBones

    return MixBones


def Mixamo_TO_Blender_Fnc(BlendBones):
    if ("mixamorig:" in BlendBones):
        if ("Left" not in BlendBones and "Right" not in BlendBones):
            BlendBones = BlendBones[10:]
        if ("Right" in BlendBones):
            BlendBones = Mixamo_TO_Blender_Rename(BlendBones, "Right", ".R")
        if ("Left" in BlendBones):
            BlendBones = Mixamo_TO_Blender_Rename(BlendBones, "Left", ".L")
            pass
    return BlendBones


class RENAME_OT_Mtob(bpy.types.Operator):
    """renames all mixamo bones to blender name conventions"""
    bl_idname = 'rename.mixtoblend'
    bl_label = "rename to blender"

    def execute(self, context):
        for bone in bpy.context.selected_pose_bones:
            bone.name = Mixamo_TO_Blender_Fnc(bone.name)

        return {'FINISHED'}
class RENAME_OT_Btom(bpy.types.Operator):
    """renames all blener bones to mixamo name conventions"""
    bl_idname = 'rename.blendtomix'
    bl_label = "rename to mixamo"

    def execute(self, context):
        for bone in bpy.context.selected_pose_bones:
            bone.name = Blender_TO_Mixamo_Fnc(bone.name)
            print(bone.name)

        return {'FINISHED'}
















