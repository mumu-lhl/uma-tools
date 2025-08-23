import bpy
import math
from mathutils import Vector, Euler
from ..config.bone_config import BONE_CONFIGS


class UMA_TOOL_OT_generate_controllers(bpy.types.Operator):
    """遍历配置列表，为所有定义的骨骼生成控制器"""

    bl_idname = "uma_tool.generate_controllers"
    bl_label = "生成控制器"
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

        ctrl_collection_name = "Controllers"
        if ctrl_collection_name not in bpy.data.collections:
            ctrl_collection = bpy.data.collections.new(ctrl_collection_name)
            context.scene.collection.children.link(ctrl_collection)
        else:
            ctrl_collection = bpy.data.collections[ctrl_collection_name]

        new_controllers = {}

        bone_custom_colors = {
            "Left": (0.0, 1.0, 1.0),  # Cyan
            "Right": (1.0, 1.0, 0.0),  # Yellow
            "Center": (1.0, 0.0, 1.0),  # Magenta
        }
        active_color = (1.0, 0.0, 0.0)  # Red

        for config in BONE_CONFIGS:
            bone = armature.data.bones.get(config.bone_name)  # pyright: ignore[reportAttributeAccessIssue]
            if not bone:
                self.report(
                    {"WARNING"}, f"数据层骨骼 '{config.bone_name}' 未找到，已跳过。"
                )
                continue

            ctrl_name = f"CTRL_{config.bone_name}"

            bone_name_low = config.bone_name.lower()
            group_name = "Center"
            if ".l" in bone_name_low or "_l" in bone_name_low:
                group_name = "Left"
            elif ".r" in bone_name_low or "_r" in bone_name_low:
                group_name = "Right"

            if hasattr(bone, "color"):
                bone.color.palette = "CUSTOM"
                color = bone_custom_colors[group_name]
                bone.color.custom.normal = color
                bone.color.custom.active = active_color
                bone.color.custom.select = color

            existing_ctrl = bpy.data.objects.get(ctrl_name)
            if existing_ctrl:
                bpy.data.objects.remove(existing_ctrl, do_unlink=True)

            bone_length = bone.length
            if bone_length < 0.001:
                bone_length = 0.1

            controller = None
            controller_size = bone_length * config.radius_multiplier

            context.view_layer.objects.active = armature

            if config.shape == "CIRCLE":
                bpy.ops.curve.primitive_bezier_circle_add(
                    radius=controller_size,
                    enter_editmode=False,
                    align="WORLD",
                    location=(0, 0, 0),
                )
                controller = context.active_object

            elif config.shape == "SQUARE":
                bpy.ops.curve.primitive_bezier_circle_add(
                    radius=controller_size,
                    enter_editmode=False,
                    align="WORLD",
                    location=(0, 0, 0),
                )
                controller = context.active_object
                context.view_layer.objects.active = controller
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.curve.select_all(action="SELECT")
                bpy.ops.curve.handle_type_set(type="VECTOR")
                bpy.ops.object.mode_set(mode="OBJECT")

            elif config.shape == "ARROW_CIRCLE":
                # 创建一个空的曲线对象来容纳所有的几何体
                bpy.ops.object.add(type="CURVE", location=(0, 0, 0))
                controller = context.active_object
                splines = controller.data.splines  # pyright: ignore[reportAttributeAccessIssue]
                # 清除默认创建的样条线
                splines.clear()

                arrow_size = controller_size * 0.4
                arrow_offset = controller_size * 1.0

                # 用于存储每个箭头基部在世界坐标系下的起点和终点
                arrow_base_points_world = []

                # 循环创建4个箭头样条线
                for i in range(4):
                    spline = splines.new("BEZIER")
                    # 定义单个箭头的局部坐标点
                    points_pos_raw: list[tuple[float, float, float]] = [
                        (-0.3, -0.05, 0),
                        (-0.3, 0.5, 0),
                        (-0.5, 0.5, 0),
                        (0, 1, 0),
                        (0.5, 0.5, 0),
                        (0.3, 0.5, 0),
                        (0.3, -0.05, 0),
                    ]

                    # 计算每个箭头的旋转和位置
                    angle = i * math.pi / 2
                    rot_matrix = Euler((0, 0, -angle), "XYZ").to_matrix()
                    location = Vector(
                        (
                            arrow_offset * math.sin(angle),
                            arrow_offset * math.cos(angle),
                            0,
                        )
                    )

                    # 将局部坐标点转换为世界坐标
                    world_points = [
                        location + rot_matrix @ (Vector(p) * arrow_size)
                        for p in points_pos_raw
                    ]

                    # 将计算好的点添加到样条线中
                    spline.bezier_points.add(len(world_points) - 1)
                    for j, p_co in enumerate(world_points):
                        p = spline.bezier_points[j]
                        p.co = p_co
                        p.handle_left_type = "VECTOR"
                        p.handle_right_type = "VECTOR"

                    # 记录下箭头基部的两个点，用于后续连接圆弧
                    arrow_base_points_world.append((world_points[0], world_points[-1]))

                # 循环创建4个圆弧样条线来连接箭头
                for i in range(4):
                    next_i = (i + 1) % 4
                    # 获取当前箭头的终点和下一个箭头的起点
                    p_start = arrow_base_points_world[i][1]
                    p_end = arrow_base_points_world[next_i][0]

                    spline = splines.new("BEZIER")
                    spline.bezier_points.add(1)
                    p0, p1 = spline.bezier_points
                    p0.co, p1.co = p_start, p_end

                    # --- 设置贝塞尔手柄以形成平滑的圆弧 ---
                    # 这个神奇数字是 (4/3)*tan(pi/8)，用于通过2个贝塞尔点创建90度圆弧
                    handle_len = controller_size * 0.55228
                    # 计算起点的手柄向量
                    v_start = p_start.normalized()
                    h_start = v_start.cross(Vector((0, 0, 1))).normalized() * handle_len
                    p0.handle_right, p0.handle_left = p0.co + h_start, p0.co - h_start
                    # 计算终点的手柄向量
                    v_end = p_end.normalized()
                    h_end = v_end.cross(Vector((0, 0, 1))).normalized() * handle_len
                    p1.handle_left, p1.handle_right = p1.co - h_end, p1.co + h_end
                    # 设置手柄类型为对齐，以确保曲线平滑
                    p0.handle_left_type = p0.handle_right_type = "ALIGNED"
                    p1.handle_left_type = p1.handle_right_type = "ALIGNED"

            if not controller:
                continue

            controller.name = ctrl_name
            new_controllers[config.bone_name] = controller

            for coll in controller.users_collection:
                coll.objects.unlink(controller)
            ctrl_collection.objects.link(controller)

        context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode="POSE")

        for config in BONE_CONFIGS:
            pose_bone = armature.pose.bones.get(config.bone_name)
            if not pose_bone:
                continue

            controller = new_controllers.get(config.bone_name)
            if not controller:
                continue

            pose_bone.custom_shape = None

            controller.matrix_world = armature.matrix_world @ pose_bone.matrix

            pose_bone.custom_shape = controller

            if config.shape_rotation_euler == "GLOBAL_HORIZONTAL":
                bone_rotation_matrix = pose_bone.matrix.to_3x3()
                inverse_rotation_matrix = bone_rotation_matrix.inverted()
                target_rotation_matrix = Euler((0, 0, 0), "XYZ").to_matrix().to_3x3()
                final_rotation_matrix = inverse_rotation_matrix @ target_rotation_matrix
                pose_bone.custom_shape_rotation_euler = final_rotation_matrix.to_euler(
                    "XYZ"
                )
            else:
                pose_bone.custom_shape_rotation_euler = config.shape_rotation_euler

            direction_vec = Vector(config.offset_direction)
            offset_vector = direction_vec * pose_bone.length * config.offset_multiplier
            pose_bone.custom_shape_translation = offset_vector

            pose_bone.use_custom_shape_bone_size = False
            armature.data.bones[pose_bone.name].show_wire = True  # pyright: ignore[reportAttributeAccessIssue]

            controller.hide_select = True
            controller.hide_viewport = True

        bpy.ops.object.mode_set(mode="OBJECT")

        self.report({"INFO"}, "控制器已清理并重新生成。")
        return {"FINISHED"}
