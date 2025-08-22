import bpy
from mathutils import Vector, Euler
from collections import namedtuple
import math

# --- 插件信息 ---
bl_info = {
    "name": "赛马娘工具",
    "author": "Gemini & Mumulhl",
    "version": (0, 1, 1), # 版本号微调
    "blender": (4, 2, 0),
    "location": "3D视图 > 侧边栏 > 赛马娘工具",
    "description": "赛马娘一键生成控制器、骨骼优化显示工具。",
    "warning": "",
    "doc_url": "",
    "category": "Rigging",
}

# --- 核心配置 ---
ControllerConfig = namedtuple(
    "ControllerConfig",
    [
        "bone_name", "shape", "radius_multiplier",
        "offset_direction", "offset_multiplier", "shape_rotation_euler"
    ]
)

# 1.5708 约等于 90 度
BONE_CONFIGS = [
    # --- 主干部分 ---
    ControllerConfig(
        bone_name="Head", shape="CIRCLE", radius_multiplier=7.0,
        offset_direction=(0, -1, 0), offset_multiplier=5.0,
        shape_rotation_euler=(0, 0, 0)
    ),
    ControllerConfig(
        bone_name="Waist", shape="CIRCLE", radius_multiplier=2.0,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Hip", shape="SQUARE", radius_multiplier=5.0,
        offset_direction=(0, -1, -1), offset_multiplier=1.5,
        shape_rotation_euler='GLOBAL_HORIZONTAL'
    ),

    # --- 右耳 ---
    ControllerConfig(
        bone_name="Ear_01_R", shape="CIRCLE", radius_multiplier=1.0,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Ear_02_R", shape="CIRCLE", radius_multiplier=0.5,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    # --- 新增 ---
    ControllerConfig(
        bone_name="Ear_03_R", shape="CIRCLE", radius_multiplier=0.3,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),

    # --- 左耳 ---
    ControllerConfig(
        bone_name="Ear_01_L", shape="CIRCLE", radius_multiplier=1.0,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Ear_02_L", shape="CIRCLE", radius_multiplier=0.5,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    # --- 新增 ---
    ControllerConfig(
        bone_name="Ear_03_L", shape="CIRCLE", radius_multiplier=0.3,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),

    # --- 右臂 ---
    ControllerConfig(
        bone_name="Shoulder_R", shape="CIRCLE", radius_multiplier=2,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Arm_R", shape="CIRCLE", radius_multiplier=1.5,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Elbow_R", shape="CIRCLE", radius_multiplier=1.0,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),

    # --- 右手 ---
    ControllerConfig(
        bone_name="Wrist_R", shape="CIRCLE", radius_multiplier=1.5,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Thumb_01_R", shape="SQUARE", radius_multiplier=1.0, offset_direction=(0, 0, 0), offset_multiplier=0.0, shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Thumb_03_R", shape="SQUARE", radius_multiplier=1.0, offset_direction=(0, 0, 0), offset_multiplier=0.0, shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Index_01_R", shape="SQUARE", radius_multiplier=1.0, offset_direction=(0, 0, 0), offset_multiplier=0.0, shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Index_03_R", shape="SQUARE", radius_multiplier=1.0, offset_direction=(0, 0, 0), offset_multiplier=0.0, shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Ring_01_R", shape="SQUARE", radius_multiplier=1.0, offset_direction=(0, 0, 0), offset_multiplier=0.0, shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Ring_03_R", shape="SQUARE", radius_multiplier=1.0, offset_direction=(0, 0, 0), offset_multiplier=0.0, shape_rotation_euler=(1.5708, 0, 0)
    ),

    # --- 左臂 ---
    ControllerConfig(
        bone_name="Shoulder_L", shape="CIRCLE", radius_multiplier=2,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Arm_L", shape="CIRCLE", radius_multiplier=1.5,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Elbow_L", shape="CIRCLE", radius_multiplier=1,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),

    # --- 左手 ---
    ControllerConfig(
        bone_name="Wrist_L", shape="CIRCLE", radius_multiplier=1.5,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Thumb_01_L", shape="SQUARE", radius_multiplier=1.0, offset_direction=(0, 0, 0), offset_multiplier=0.0, shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Thumb_03_L", shape="SQUARE", radius_multiplier=1.0, offset_direction=(0, 0, 0), offset_multiplier=0.0, shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Index_01_L", shape="SQUARE", radius_multiplier=1.0, offset_direction=(0, 0, 0), offset_multiplier=0.0, shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Index_03_L", shape="SQUARE", radius_multiplier=1.0, offset_direction=(0, 0, 0), offset_multiplier=0.0, shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Ring_01_L", shape="SQUARE", radius_multiplier=1.0, offset_direction=(0, 0, 0), offset_multiplier=0.0, shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Ring_03_L", shape="SQUARE", radius_multiplier=1.0, offset_direction=(0, 0, 0), offset_multiplier=0.0, shape_rotation_euler=(1.5708, 0, 0)
    ),

    # --- 右腿 ---
    ControllerConfig(
        bone_name="Thigh_R", shape="CIRCLE", radius_multiplier=1.0,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Knee_R", shape="CIRCLE", radius_multiplier=0.8,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Ankle_R", shape="CIRCLE", radius_multiplier=0.4,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),

    # --- 左腿 ---
    ControllerConfig(
        bone_name="Thigh_L", shape="CIRCLE", radius_multiplier=1,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Knee_L", shape="CIRCLE", radius_multiplier=0.8,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Ankle_L", shape="CIRCLE", radius_multiplier=0.4,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),

    # --- 尾巴 ---
    ControllerConfig(
        bone_name="Sp_Hi_Tail0_B_00", shape="CIRCLE", radius_multiplier=1,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Sp_Hi_Tail0_B_01", shape="CIRCLE", radius_multiplier=0.8,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
    ControllerConfig(
        bone_name="Sp_Hi_Tail0_B_02", shape="CIRCLE", radius_multiplier=0.4,
        offset_direction=(0, 0, 0), offset_multiplier=0.0,
        shape_rotation_euler=(1.5708, 0, 0)
    ),
]

# --- 已重构和修复的 Operator ---
class UMA_TOOL_OT_generate_controllers(bpy.types.Operator):
    """遍历配置列表，为所有定义的骨骼生成控制器"""
    bl_idname = "uma_tool.generate_controllers"
    bl_label = "生成控制器"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        armature = context.active_object
        
        # 确保在 OBJECT 模式下执行清理和创建
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # 准备控制器集合
        ctrl_collection_name = "Controllers"
        if ctrl_collection_name not in bpy.data.collections:
            ctrl_collection = bpy.data.collections.new(ctrl_collection_name)
            context.scene.collection.children.link(ctrl_collection)
        else:
            ctrl_collection = bpy.data.collections[ctrl_collection_name]

        # 存储新创建的控制器，键为骨骼名，值为控制器对象
        new_controllers = {}

        # --- 第一阶段：在物体模式下清理旧的并创建新的控制器 ---
        for config in BONE_CONFIGS:
            bone = armature.data.bones.get(config.bone_name)
            if not bone:
                self.report({'WARNING'}, f"数据层骨骼 '{config.bone_name}' 未找到，已跳过。")
                continue

            ctrl_name = f"CTRL_{config.bone_name}"
            
            # 清理可能存在的旧控制器
            existing_ctrl = bpy.data.objects.get(ctrl_name)
            if existing_ctrl:
                bpy.data.objects.remove(existing_ctrl, do_unlink=True)
            
            bone_length = bone.length
            if bone_length < 0.001: bone_length = 0.1

            # 创建新的控制器
            controller = None
            controller_size = bone_length * config.radius_multiplier
            
            # 激活骨架，以防万一活动物体是别的
            context.view_layer.objects.active = armature
            
            if config.shape == 'CIRCLE':
                bpy.ops.curve.primitive_bezier_circle_add(radius=controller_size, enter_editmode=False, align='WORLD', location=(0, 0, 0))
                controller = context.active_object
            elif config.shape == 'SQUARE':
                bpy.ops.curve.primitive_bezier_circle_add(radius=controller_size, enter_editmode=False, align='WORLD', location=(0, 0, 0))
                controller = context.active_object
                context.view_layer.objects.active = controller # 确保控制器是活动对象以进入编辑模式
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.curve.select_all(action='SELECT')
                bpy.ops.curve.handle_type_set(type='VECTOR')
                bpy.ops.object.mode_set(mode='OBJECT')

            if not controller:
                continue
            
            controller.name = ctrl_name 
            new_controllers[config.bone_name] = controller

            # 将控制器放入集合
            for coll in controller.users_collection:
                coll.objects.unlink(controller)
            ctrl_collection.objects.link(controller)

        # --- 第二阶段：进入姿态模式一次，然后分配所有属性 ---
        context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        
        for config in BONE_CONFIGS:
            pose_bone = armature.pose.bones.get(config.bone_name)
            if not pose_bone:
                continue

            # 从我们的字典中获取新创建的控制器
            controller = new_controllers.get(config.bone_name)
            if not controller:
                continue

            # 清除旧的 custom_shape 引用（以防万一）
            pose_bone.custom_shape = None

            # 匹配控制器位置和骨骼位置
            controller.matrix_world = armature.matrix_world @ pose_bone.matrix
            
            # 分配新的 custom_shape
            pose_bone.custom_shape = controller
            
            # 设置旋转
            if config.shape_rotation_euler == 'GLOBAL_HORIZONTAL':
                bone_rotation_matrix = pose_bone.matrix.to_3x3()
                inverse_rotation_matrix = bone_rotation_matrix.inverted()
                # 目标是世界水平，所以局部旋转为0
                target_rotation_matrix = Euler((0, 0, 0), 'XYZ').to_matrix().to_3x3()
                final_rotation_matrix = inverse_rotation_matrix @ target_rotation_matrix
                pose_bone.custom_shape_rotation_euler = final_rotation_matrix.to_euler('XYZ')
            else:
                pose_bone.custom_shape_rotation_euler = config.shape_rotation_euler

            # 设置偏移
            direction_vec = Vector(config.offset_direction)
            offset_vector = direction_vec * pose_bone.length * config.offset_multiplier
            pose_bone.custom_shape_translation = offset_vector
            
            # 其他属性设置
            pose_bone.use_custom_shape_bone_size = False
            armature.data.bones[pose_bone.name].show_wire = True

            # 隐藏控制器物体本身
            controller.hide_select = True
            controller.hide_viewport = True
        
        # --- 完成后，返回物体模式 ---
        bpy.ops.object.mode_set(mode='OBJECT')
        
        self.report({'INFO'}, f"控制器已清理并重新生成。")
        return {'FINISHED'}


class UMA_TOOL_OT_optimize_skeleton_display(bpy.types.Operator):
    """隐藏所有以 _Handle 结尾的骨骼和指定的耳朵骨骼"""
    bl_idname = "uma_tool.optimize_skeleton_display"
    bl_label = "优化骨骼显示"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        armature = context.active_object
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        hidden_count = 0
        bones_to_hide = ["Sp_He_Ear0_R_01", "Sp_He_Ear0_R_02", "Sp_He_Ear0_L_01", "Sp_He_Ear0_L_02"]
        for bone in armature.data.bones:
            if bone.name.endswith("_Handle") or bone.name in bones_to_hide:
                bone.hide = True
                hidden_count += 1
        
        self.report({'INFO'}, f"已隐藏 {hidden_count} 根骨骼。")
        return {'FINISHED'}


class UMA_TOOL_OT_revert_skeleton_display(bpy.types.Operator):
    """显示所有以 _Handle 结尾的骨骼和指定的耳朵骨骼"""
    bl_idname = "uma_tool.revert_skeleton_display"
    bl_label = "反向优化骨骼显示"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        armature = context.active_object
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        shown_count = 0
        bones_to_show = ["Sp_He_Ear0_R_01", "Sp_He_Ear0_R_02", "Sp_He_Ear0_L_01", "Sp_He_Ear0_L_02"]
        for bone in armature.data.bones:
            if bone.name.endswith("_Handle") or bone.name in bones_to_show:
                bone.hide = False
                shown_count += 1

        self.report({'INFO'}, f"已显示 {shown_count} 根骨骼。")
        return {'FINISHED'}


class UMA_TOOL_PT_main_panel(bpy.types.Panel):
    bl_label = "骨骼工具"
    bl_idname = "UMA_TOOL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '赛马娘工具'

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="控制器生成")
        box.operator(UMA_TOOL_OT_generate_controllers.bl_idname)
        
        box = layout.box()
        box.label(text="骨架显示")
        box.operator(UMA_TOOL_OT_optimize_skeleton_display.bl_idname)
        box.operator(UMA_TOOL_OT_revert_skeleton_display.bl_idname)


classes = (
    UMA_TOOL_OT_generate_controllers,
    UMA_TOOL_OT_optimize_skeleton_display,
    UMA_TOOL_OT_revert_skeleton_display,
    UMA_TOOL_PT_main_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    try:
        unregister()
    except Exception:
        pass
    register()
