import bpy
import os

# === 配置 ===
input_dae_path = "/home/diligent/四轮四驱100_0.1_精细(1)/四轮四驱100_0.0_乐聚_精细/four_ws_robot/fourth_robot_description/meshes/DAE/base/dipanAndshengjiang.dae"   # 修改为你的输入路径
output_dae_path = "/home/diligent/四轮四驱100_0.1_精细(1)/四轮四驱100_0.0_乐聚_精细/four_ws_robot/fourth_robot_description/meshes/DAE/base/small15.dae" # 修改为你的输出路径
decimate_ratio = 0.15  # 减面比例，0.5 表示保留一半面

# === 清除当前场景 ===
bpy.ops.wm.read_factory_settings(use_empty=True)

# === 导入 DAE 文件 ===
bpy.ops.wm.collada_import(filepath=input_dae_path)

# === 遍历所有 mesh 对象并进行 decimation ===
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        # 设置为活动对象
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # 添加 Decimate 修改器
        decimate = obj.modifiers.new(name='DecimateMod', type='DECIMATE')
        decimate.ratio = decimate_ratio
        decimate.use_collapse_triangulate = True  # 可选：三角化避免拓扑问题

        # 应用修改器
        bpy.ops.object.modifier_apply(modifier=decimate.name)

        obj.select_set(False)

# === 导出为 DAE 文件 ===
bpy.ops.wm.collada_export(filepath=output_dae_path,
                          apply_modifiers=True,
                          selected=False)

print("✅ DAE 文件简化并导出完成！")
