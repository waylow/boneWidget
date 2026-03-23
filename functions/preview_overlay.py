"""
Bone Widget 预览线绘制模块
使用 GPU 在空间中绘制自定义骨骼的虚线预览
"""

import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Matrix, Vector

# 全局状态
PREVIEW_HANDLER = None
PREVIEW_WIDGET_DATA = None
PREVIEW_BONE = None


def draw_widget_preview():
    """在 3D 视图中绘制 widget 预览线"""
    global PREVIEW_WIDGET_DATA, PREVIEW_BONE
    
    if not PREVIEW_WIDGET_DATA or not PREVIEW_BONE:
        return
    
    context = bpy.context
    
    # 获取 widget 数据
    widget_data = PREVIEW_WIDGET_DATA
    
    # 构建线条数据
    lines = []
    
    # 获取顶点和边
    vertices = widget_data.get('vertices', [])
    edges = widget_data.get('edges', [])
    
    if not vertices or not edges:
        return
    
    # 计算变换矩阵
    armature = PREVIEW_BONE.id_data
    bone = PREVIEW_BONE.bone
    
    # 基础变换：骨骼位置
    matrix = armature.matrix_world @ bone.matrix_local
    
    # 应用 CloudRig 控件的变换（如果有）
    if hasattr(PREVIEW_BONE, 'custom_shape_transform') and PREVIEW_BONE.custom_shape_transform:
        matrix = armature.matrix_world @ PREVIEW_BONE.custom_shape_transform.bone.matrix_local
    
    # 应用 Bone Widget 的变换参数
    loc = PREVIEW_BONE.custom_shape_translation
    rot = PREVIEW_BONE.custom_shape_rotation_euler
    scale = PREVIEW_BONE.custom_shape_scale_xyz.copy()
    
    if PREVIEW_BONE.use_custom_shape_bone_size:
        scale *= bone.length
    
    custom_matrix = Matrix.LocRotScale(loc, rot, scale)
    matrix = matrix @ custom_matrix
    
    # 转换顶点并构建线条
    transformed_verts = [matrix @ Vector(v) for v in vertices]
    
    for edge in edges:
        if len(edge) == 2:
            v1 = transformed_verts[edge[0]]
            v2 = transformed_verts[edge[1]]
            lines.append((v1, v2))
    
    if not lines:
        return
    
    # 创建 GPU Batch
    shader = gpu.shader.from_builtin('POLYLINE_FLAT_COLOR')
    shader.bind()
    
    # 设置视口大小
    shader.uniform_float("viewportSize", gpu.state.viewport_get()[2:])
    
    # 设置线宽
    if bpy.app.version >= (4, 2, 0):
        line_width = PREVIEW_BONE.custom_shape_wire_width
    else:
        line_width = 2.0
    shader.uniform_float("lineWidth", line_width)
    
    # 准备顶点数据（虚线效果）
    dash_length = 0.05  # 虚线段长度
    positions = []
    colors = []
    
    # 主题颜色
    theme = context.preferences.themes["Default"]
    color_normal = theme.bone_color_sets[0].normal
    color = (color_normal.r, color_normal.g, color_normal.b, 0.8)  # 80% 透明度
    
    for start, end in lines:
        # 计算虚线
        direction = (end - start).normalized()
        length = (end - start).length
        
        if length < 0.0001:
            continue
        
        num_segments = max(1, int(length / dash_length))
        
        for i in range(num_segments):
            # 只绘制偶数段，形成虚线效果
            if i % 2 == 0:
                seg_start = start + direction * (i * dash_length)
                seg_end = start + direction * (min((i + 1) * dash_length, length))
                positions.extend([seg_start, seg_end])
                colors.extend([color, color])
    
    if positions:
        batch = batch_for_shader(shader, 'LINES', {"pos": positions, "color": colors})
        batch.draw(shader)


def enable_widget_preview(bone, widget_data):
    """启用 widget 预览线绘制
    
    Args:
        bone: 目标骨骼 (PoseBone)
        widget_data: widget 数据字典，包含 'vertices' 和 'edges'
    """
    global PREVIEW_HANDLER, PREVIEW_WIDGET_DATA, PREVIEW_BONE
    
    # 禁用之前的预览
    disable_widget_preview()
    
    PREVIEW_WIDGET_DATA = widget_data
    PREVIEW_BONE = bone
    
    # 添加绘制处理器
    if PREVIEW_HANDLER is None:
        PREVIEW_HANDLER = bpy.types.SpaceView3D.draw_handler_add(
            draw_widget_preview,
            (),
            'WINDOW',
            'POST_VIEW'
        )
    
    # 强制刷新视图
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()


def disable_widget_preview():
    """禁用 widget 预览线绘制"""
    global PREVIEW_HANDLER, PREVIEW_WIDGET_DATA, PREVIEW_BONE
    
    if PREVIEW_HANDLER is not None:
        bpy.types.SpaceView3D.draw_handler_remove(PREVIEW_HANDLER, 'WINDOW')
        PREVIEW_HANDLER = None
    
    PREVIEW_WIDGET_DATA = None
    PREVIEW_BONE = None
    
    # 强制刷新视图
    if bpy.context and bpy.context.screen:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def update_widget_preview(bone, widget_data):
    """更新预览线数据
    
    Args:
        bone: 目标骨骼 (PoseBone)
        widget_data: widget 数据字典
    """
    global PREVIEW_WIDGET_DATA, PREVIEW_BONE
    
    PREVIEW_WIDGET_DATA = widget_data
    PREVIEW_BONE = bone
    
    # 刷新视图
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()


def is_preview_active():
    """检查预览是否处于活动状态"""
    return PREVIEW_HANDLER is not None


def register():
    """注册模块"""
    pass


def unregister():
    """注销模块"""
    disable_widget_preview()
