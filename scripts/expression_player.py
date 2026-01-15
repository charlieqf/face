# scripts/expression_player.py
"""
表情序列播放器 - 读取 CSV 并逐帧发送 TTL 指令
"""
import sys
import time
import pandas as pd
sys.path.insert(0, '.')

from src.hardware.robot_controller import RobotController

def play_expression_sequence(csv_path: str, delay: float = 0.3):
    """
    播放表情序列
    
    Args:
        csv_path: CSV 文件路径，包含 char, mouth, eye, lid 列
        delay: 每帧间隔秒数
    """
    robot = RobotController(mock=True)
    df = pd.read_csv(csv_path)
    
    print("=" * 60)
    print("表情序列播放开始")
    print("=" * 60)
    print(f"{'字符':<4} {'嘴巴':<6} {'眼球':<6} {'眼皮':<6} TTL指令")
    print("-" * 60)
    
    for _, row in df.iterrows():
        char = row['char']
        mouth = int(row['mouth'])
        eye = int(row['eye'])
        lid = int(row['lid'])
        
        # 发送指令
        robot.set_mouth(mouth)
        robot.set_eye_position(eye)
        robot.set_eyelid(lid)
        
        # 显示当前帧
        print(f"{char:<4} {mouth:<6} {eye:<6} {lid:<6}", end="")
        print(f"#DGM:{mouth}! $DGB:{eye}! $DGL:{lid}!")
        
        time.sleep(delay)
    
    print("=" * 60)
    print("播放结束")
    robot.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='播放表情序列')
    parser.add_argument('csv', nargs='?', default='data/expression_sequence_manual.csv',
                        help='CSV 文件路径')
    parser.add_argument('--delay', type=float, default=0.3, help='帧间隔(秒)')
    args = parser.parse_args()
    
    play_expression_sequence(args.csv, args.delay)
