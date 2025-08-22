import bpy
from ..operators.generate_controllers import UMA_TOOL_OT_generate_controllers
from ..operators.optimize_skeleton_display import UMA_TOOL_OT_optimize_skeleton_display
from ..operators.revert_skeleton_display import UMA_TOOL_OT_revert_skeleton_display


class UMA_TOOL_PT_main_panel(bpy.types.Panel):
    bl_label = "骨骼工具"
    bl_idname = "UMA_TOOL_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "赛马娘工具"

    def draw(self, context):
        layout = self.layout

        is_armature_selected = (
            context.active_object is not None
            and context.active_object.type == "ARMATURE"
        )

        layout.enabled = is_armature_selected

        box = layout.box()
        box.label(text="控制器生成")
        box.operator(UMA_TOOL_OT_generate_controllers.bl_idname)

        box = layout.box()
        box.label(text="骨架显示")
        box.operator(UMA_TOOL_OT_optimize_skeleton_display.bl_idname)
        box.operator(UMA_TOOL_OT_revert_skeleton_display.bl_idname)
