import bpy

from bpy.types import Menu


def get_or_create_eye_or_mouth_position_nodegroup():
    """Ensures the '眼睛/嘴巴位置' node group exists and returns it."""
    group_name = "眼睛/嘴巴位置"

    if group_name in bpy.data.node_groups:
        return bpy.data.node_groups[group_name]

    # Create the node group
    group = bpy.data.node_groups.new(name=group_name, type="ShaderNodeTree")

    # --- Group Interface ---
    socket_in = group.interface.new_socket(
        name="编号", in_out="INPUT", socket_type="NodeSocketInt"
    )
    socket_in.default_value = 1  # pyright: ignore[reportAttributeAccessIssue]

    group.interface.new_socket(name="矢量", in_out="INPUT", socket_type="NodeSocketVector")

    group.interface.new_socket(
        name="矢量", in_out="OUTPUT", socket_type="NodeSocketVector"
    )

    # --- Nodes ---
    group_input_node = group.nodes.new("NodeGroupInput")
    group_input_node.location = (-800, 0)

    group_output_node = group.nodes.new("NodeGroupOutput")
    group_output_node.location = (600, 0)

    subtract_node = group.nodes.new("ShaderNodeMath")
    subtract_node.name = "相减"
    subtract_node.label = "相减"
    subtract_node.operation = "SUBTRACT"  # pyright: ignore[reportAttributeAccessIssue]
    subtract_node.inputs[1].default_value = 1.0  # pyright: ignore[reportAttributeAccessIssue]
    subtract_node.location = (-600, 100)

    column_node = group.nodes.new("ShaderNodeMath")
    column_node.name = "列号"
    column_node.label = "列号"
    column_node.operation = "MODULO"  # pyright: ignore[reportAttributeAccessIssue]
    column_node.inputs[1].default_value = 4.0  # pyright: ignore[reportAttributeAccessIssue]
    column_node.location = (-400, 200)

    row_node = group.nodes.new("ShaderNodeMath")
    row_node.name = "行号"
    row_node.label = "行号"
    row_node.operation = "DIVIDE"  # pyright: ignore[reportAttributeAccessIssue]
    row_node.inputs[1].default_value = 4.0  # pyright: ignore[reportAttributeAccessIssue]
    row_node.location = (-400, 0)

    floor_node = group.nodes.new("ShaderNodeMath")
    floor_node.name = "向下取整"
    floor_node.label = "向下取整"
    floor_node.operation = "FLOOR"  # pyright: ignore[reportAttributeAccessIssue]
    floor_node.location = (-200, 0)

    x_offset_node = group.nodes.new("ShaderNodeMath")
    x_offset_node.name = "X偏移"
    x_offset_node.label = "X偏移"
    x_offset_node.operation = "MULTIPLY"  # pyright: ignore[reportAttributeAccessIssue]
    x_offset_node.inputs[1].default_value = 0.25  # pyright: ignore[reportAttributeAccessIssue]
    x_offset_node.location = (-200, 200)

    y_offset_node = group.nodes.new("ShaderNodeMath")
    y_offset_node.name = "Y偏移"
    y_offset_node.label = "Y偏移"
    y_offset_node.operation = "MULTIPLY"  # pyright: ignore[reportAttributeAccessIssue]
    y_offset_node.inputs[1].default_value = -0.125  # pyright: ignore[reportAttributeAccessIssue]
    y_offset_node.location = (0, 0)

    combine_xyz_node = group.nodes.new("ShaderNodeCombineXYZ")
    combine_xyz_node.name = "合并XYZ"
    combine_xyz_node.label = "合并XYZ"
    combine_xyz_node.inputs[2].default_value = 0.0  # pyright: ignore[reportAttributeAccessIssue]
    combine_xyz_node.location = (200, 100)

    mapping_node = group.nodes.new("ShaderNodeMapping")
    mapping_node.location = (400, 100)

    # --- Links ---
    links = group.links
    links.new(group_input_node.outputs["编号"], subtract_node.inputs[0])
    links.new(subtract_node.outputs["Value"], column_node.inputs[0])
    links.new(subtract_node.outputs["Value"], row_node.inputs[0])
    links.new(row_node.outputs["Value"], floor_node.inputs[0])
    links.new(column_node.outputs["Value"], x_offset_node.inputs[0])
    links.new(floor_node.outputs["Value"], y_offset_node.inputs[0])
    links.new(x_offset_node.outputs["Value"], combine_xyz_node.inputs["X"])
    links.new(y_offset_node.outputs["Value"], combine_xyz_node.inputs["Y"])
    links.new(group_input_node.outputs["矢量"], mapping_node.inputs["Vector"])
    links.new(combine_xyz_node.outputs["Vector"], mapping_node.inputs["Location"])
    links.new(mapping_node.outputs["Vector"], group_output_node.inputs["矢量"])

    return group


class UMA_OT_AddEyeOrMoutnhPositionNode(bpy.types.Operator):
    """Adds the '眼睛/嘴巴位置' node group to the active shader tree."""

    bl_idname = "uma.add_eye_position_node"
    bl_label = "眼睛/嘴巴位置"
    bl_description = "添加一个眼睛/嘴巴位置节点组"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (
            space.type == "NODE_EDITOR"
            and space.shader_type == "OBJECT"  # pyright: ignore[reportAttributeAccessIssue]
            and context.object.active_material is not None
        )

    def execute(self, context):  # pyright: ignore[reportIncompatibleMethodOverride]
        group = get_or_create_eye_or_mouth_position_nodegroup()

        node = context.space_data.edit_tree.nodes.new(type="ShaderNodeGroup")  # pyright: ignore[reportAttributeAccessIssue]
        node.node_tree = group
        node.name = group.name
        node.label = group.name

        node.location = context.space_data.cursor_location  # pyright: ignore[reportAttributeAccessIssue]
        node.select = True
        context.space_data.edit_tree.nodes.active = node  # pyright: ignore[reportAttributeAccessIssue]

        return {"FINISHED"}


class UMA_MT_node_add_menu(Menu):
    bl_label = "赛马娘工具"
    bl_idname = "UMA_MT_node_add_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator(
            UMA_OT_AddEyeOrMoutnhPositionNode.bl_idname, text=UMA_OT_AddEyeOrMoutnhPositionNode.bl_label
        )


def add_to_node_menu(self, context):
    self.layout.menu(UMA_MT_node_add_menu.bl_idname, text="赛马娘工具")


def register():
    bpy.utils.register_class(UMA_OT_AddEyeOrMoutnhPositionNode)
    bpy.utils.register_class(UMA_MT_node_add_menu)
    bpy.types.NODE_MT_add.append(add_to_node_menu)


def unregister():
    bpy.utils.unregister_class(UMA_OT_AddEyeOrMoutnhPositionNode)
    bpy.utils.unregister_class(UMA_MT_node_add_menu)
    bpy.types.NODE_MT_add.remove(add_to_node_menu)