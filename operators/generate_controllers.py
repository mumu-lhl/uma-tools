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
                bpy.ops.curve.primitive_bezier_circle_add(
                    radius=controller_size,
                    enter_editmode=False,
                    align="WORLD",
                    location=(0, 0, 0),
                )
                controller = context.active_object

                objects_to_join = [controller]

                arrow_size = controller_size * 0.4
                arrow_offset = controller_size * 1.0

                for i in range(4):
                    bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True)
                    arrow = context.active_object

                    bpy.ops.curve.subdivide(number_cuts=5)
                    spline = arrow.data.splines[0]  # pyright: ignore[reportAttributeAccessIssue]

                    points_pos: list[tuple[float, float, float]] = [
                        (-0.3, -0.05, 0),
                        (-0.3, 0.5, 0),
                        (-0.5, 0.5, 0),
                        (0, 1, 0),
                        (0.5, 0.5, 0),
                        (0.3, 0.5, 0),
                        (0.3, -0.05, 0),
                    ]
                    for j, pos in enumerate(points_pos):
                        point = spline.bezier_points[j]
                        point.co = Vector(pos) * arrow_size
                        point.handle_left_type = "VECTOR"
                        point.handle_right_type = "VECTOR"

                    bpy.ops.object.mode_set(mode="OBJECT")

                    angle = i * math.pi / 2
                    arrow.rotation_euler.z = -angle
                    arrow.location.x = arrow_offset * math.sin(angle)
                    arrow.location.y = arrow_offset * math.cos(angle)

                    objects_to_join.append(arrow)

                context.view_layer.objects.active = controller
                for obj in context.selected_objects:
                    obj.select_set(False)

                for obj in objects_to_join:
                    obj.select_set(True)

                bpy.ops.object.join()

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
