import bpy
import importlib

bl_info = {
    "name": "赛马娘工具",
    "author": "Gemini & Mumulhl",
    "version": (0, 1, 0),
    "blender": (4, 2, 0),
    "location": "3D视图 > 侧边栏 > 赛马娘工具",
    "description": "赛马娘一键生成控制器、骨骼优化显示工具、着色器节点组。",
    "warning": "",
    "doc_url": "",
    "category": "Rigging",
}

# 模块列表
modules_to_load = [
    ".config.bone_config",
    ".operators.generate_controllers",
    ".operators.optimize_skeleton_display",
    ".operators.revert_skeleton_display",
    ".operators.create_shader_nodes",
    ".ui.main_panel",
]

loaded_modules = []
classes_to_register = []


def reload_modules():
    """重新加载所有模块"""
    global loaded_modules
    loaded_modules.clear()
    for module_name in modules_to_load:
        module = importlib.import_module(module_name, __name__)
        importlib.reload(module)
        loaded_modules.append(module)


def register():
    """注册所有类和模块"""
    reload_modules()

    global classes_to_register
    classes_to_register.clear()

    for module in loaded_modules:
        if hasattr(module, "register"):
            module.register()
        else:
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(
                    obj, (bpy.types.Operator, bpy.types.Panel)
                ):
                    if hasattr(obj, "bl_idname"):
                        classes_to_register.append(obj)

    classes_to_register.sort(
        key=lambda cls: (issubclass(cls, bpy.types.Panel), cls.__name__)
    )

    for cls in classes_to_register:
        try:
            bpy.utils.register_class(cls)
        except ValueError as e:
            print(f"Could not register class {cls.__name__}: {e}")


def unregister():
    """注销所有类和模块"""
    # Call unregister on modules that have it FIRST
    for module in loaded_modules:
        if hasattr(module, "unregister"):
            module.unregister()

    # Then unregister the auto-discovered classes
    global classes_to_register
    for cls in reversed(classes_to_register):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except RuntimeError as e:
                print(f"Could not unregister class {cls.__name__}: {e}")
    classes_to_register.clear()


if __name__ == "__main__":
    register()
