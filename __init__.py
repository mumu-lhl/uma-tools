import bpy
import importlib

bl_info = {
    "name": "赛马娘工具",
    "author": "Gemini & Mumulhl",
    "version": (0, 1, 2),
    "blender": (4, 2, 0),
    "location": "3D视图 > 侧边栏 > 赛马娘工具",
    "description": "赛马娘一键生成控制器、骨骼优化显示工具。",
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
    ".ui.main_panel",
]

loaded_modules = []
classes = []


def reload_modules():
    """重新加载所有模块"""
    global loaded_modules
    loaded_modules.clear()
    for module_name in modules_to_load:
        module = importlib.import_module(module_name, __name__)
        importlib.reload(module)
        loaded_modules.append(module)


def register():
    """注册所有类"""
    reload_modules()

    global classes
    classes.clear()

    # 从加载的模块中收集类
    for module in loaded_modules:
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and (
                issubclass(obj, bpy.types.Operator) or issubclass(obj, bpy.types.Panel)
            ):
                if obj.bl_idname:
                    classes.append(obj)

    # 排序以确保 Panel 最后注册 (如果需要)
    classes.sort(
        key=lambda cls: (isinstance(cls.mro()[0], bpy.types.Panel), cls.__name__)
    )

    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError as e:
            print(f"Could not register class {cls.__name__}: {e}")


def unregister():
    """注销所有类"""
    global classes
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            try:
                bpy.utils.unregister_class(cls)
            except RuntimeError as e:
                print(f"Could not unregister class {cls.__name__}: {e}")
    classes.clear()


if __name__ == "__main__":
    register()
