# src/mapping/arkit_mapper.py
import numpy as np

# 简化的 ARKit 到 3 电机映射
def map_arkit_to_robot(blendshapes: dict) -> dict:
    """
    将 ARKit blendshape 字典映射到机器人指令参数。
    
    Args:
        blendshapes: 包含如 'jawOpen', 'eyeBlinkLeft' 等键的字典 (0.0-1.0)
    
    Returns:
        dict: {'mouth': 1-5, 'eye_pos': 1-21, 'eyelid': 1-4}
    """
    # 1. 嘴巴映射
    jaw_open = blendshapes.get('jawOpen', 0.0)
    mouth_level = 1 + int(jaw_open * 4)  # 0.0->1, 1.0->5

    # 2. 眼皮映射
    blink_l = blendshapes.get('eyeBlinkLeft', 0.0)
    blink_r = blendshapes.get('eyeBlinkRight', 0.0)
    avg_blink = (blink_l + blink_r) / 2
    if avg_blink > 0.7:
        lid_state = 3  # 闭眼
    elif avg_blink > 0.3:
        lid_state = 2  # 眯眼
    else:
        lid_state = 1  # 正常

    # 3. 眼球映射 (使用 5x5 网格的简化模型)
    #    参考 docs/hardware/眼球运动.png
    look_up = blendshapes.get('eyeLookUpLeft', 0.0)
    look_down = blendshapes.get('eyeLookDownLeft', 0.0)
    look_left = blendshapes.get('eyeLookOutLeft', 0.0)
    look_right = blendshapes.get('eyeLookInLeft', 0.0)
    
    # 计算行列 (1-5 范围)
    row = 3  # 默认中心行
    col = 3  # 默认中心列
    
    if look_up > 0.3: row = max(1, 3 - int(look_up * 2))
    if look_down > 0.3: row = min(5, 3 + int(look_down * 2))
    if look_left > 0.3: col = max(1, 3 - int(look_left * 2))
    if look_right > 0.3: col = min(5, 3 + int(look_right * 2))
    
    # 将 (row, col) 转换为位置 ID (1-21)
    # 假设是简单的线性排列: id = (row - 1) * 5 + col - 1, 再 +1 归一化
    eye_pos = (row - 1) * 5 + col - 1
    eye_pos = max(1, min(21, eye_pos + 1))

    return {
        "mouth": mouth_level,
        "eye_pos": eye_pos,
        "eyelid": lid_state
    }

if __name__ == "__main__":
    # 模拟 ARKit 输入
    simulated_arkit = {
        'jawOpen': 0.6,
        'eyeBlinkLeft': 0.1,
        'eyeBlinkRight': 0.1,
        'eyeLookUpLeft': 0.5,
        'eyeLookOutLeft': 0.2,
    }
    result = map_arkit_to_robot(simulated_arkit)
    print(f"模拟 ARKit 输入: {simulated_arkit}")
    print(f"机器人指令参数: {result}")
