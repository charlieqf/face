# scripts/voice_demo_adapter.py
"""
Voice_Driven_Humanoid_Head 适配层
将其语音交互逻辑适配到我们的 3 电机系统
"""
import sys
import time
sys.path.insert(0, '.')

from src.hardware.robot_controller import RobotController

class VoiceDemoAdapter:
    """
    模拟 Voice_Driven_Humanoid_Head 的语音交互流程，
    但使用我们的 RobotController 发送指令
    """
    
    def __init__(self):
        self.robot = RobotController(mock=True)
        print("=== Voice Demo Adapter 初始化完成 ===")
    
    def simulate_listening(self):
        """模拟：等待用户语音输入"""
        print("\n[状态] 正在聆听...")
        self.robot.set_eyelid(1)  # 正常睁眼
        self.robot.set_eye_position(11)  # 眼球居中
        time.sleep(0.5)
    
    def simulate_thinking(self):
        """模拟：处理语音/生成回复"""
        print("[状态] 正在思考...")
        # 眼睛往上看，表示"思考"
        self.robot.set_eye_position(3)  # 往上看
        self.robot.set_eyelid(2)  # 眯眼
        time.sleep(0.5)
    
    def simulate_speaking(self, text: str):
        """模拟：机器人说话时的嘴部动画"""
        print(f"[状态] 正在说话: '{text}'")
        self.robot.set_eyelid(1)  # 恢复正常
        self.robot.set_eye_position(11)  # 眼球居中
        
        # 模拟说话时嘴巴的开合
        # 在真实系统中，这会根据音频波形来控制
        words = text.split()
        for i, word in enumerate(words):
            # 简单模拟：根据单词长度决定张嘴程度
            mouth_level = min(5, 2 + len(word) // 3)
            self.robot.set_mouth(mouth_level)
            time.sleep(0.15)
            self.robot.set_mouth(1)  # 闭嘴
            time.sleep(0.1)
        
        print("[状态] 说话结束")
    
    def run_demo_loop(self):
        """运行一次完整的交互演示"""
        print("\n" + "="*50)
        print("开始模拟语音交互循环")
        print("="*50)
        
        # 1. 聆听
        self.simulate_listening()
        
        # 2. 模拟接收到语音 "你好，请问今天天气怎么样？"
        user_input = "你好，请问今天天气怎么样？"
        print(f"\n[用户输入] {user_input}")
        
        # 3. 思考
        self.simulate_thinking()
        
        # 4. 回复
        response = "今天天气晴朗，温度大约二十度，适合外出活动。"
        self.simulate_speaking(response)
        
        print("\n=== 演示完成 ===")
        self.robot.close()

if __name__ == "__main__":
    adapter = VoiceDemoAdapter()
    adapter.run_demo_loop()
