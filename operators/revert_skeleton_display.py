import bpy


class UMA_TOOL_OT_revert_skeleton_display(bpy.types.Operator):
    """显示所有以 _Handle 结尾的骨骼和指定的耳朵骨骼"""

    bl_idname = "uma_tool.revert_skeleton_display"
    bl_label = "反向优化骨骼显示"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "ARMATURE"
        )

    def execute(self, context):  # pyright: ignore[reportIncompatibleMethodOverride]
        armature = context.active_object
        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        shown_count = 0
        bones_to_show = [
            "Sp_He_Ear0_R_01",
            "Sp_He_Ear0_R_02",
            "Sp_He_Ear0_L_01",
            "Sp_He_Ear0_L_02",
        ]
        for bone in armature.data.bones:  # pyright: ignore[reportAttributeAccessIssue]
            if bone.name.endswith("_Handle") or bone.name in bones_to_show:
                bone.hide = False
                shown_count += 1

        self.report({"INFO"}, f"已显示 {shown_count} 根骨骼。")
        return {"FINISHED"}
