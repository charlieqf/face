# src/hardware/robot_controller.py
from src.hardware.serial_port import SerialPortMock

class RobotController:
    """硬件抽象层 (HAL)：封装所有与机器人头通信的底层细节"""

    def __init__(self, port='COM3', baudrate=9600, mock=True):
        if mock:
            self._conn = SerialPortMock(port, baudrate)
        else:
            # 当有硬件时，取消下面这行的注释
            # import serial
            # self._conn = serial.Serial(port, baudrate)
            raise NotImplementedError("真实硬件模式尚未实现")
        self._mouth_state = 1
        self._eye_state = 11 # 中心位置
        self._lid_state = 1

    def set_mouth(self, level: int):
        """设置嘴巴张开程度 (1-5)"""
        level = max(1, min(5, level))
        self._mouth_state = level
        self._conn.write(f"#DGM:{level}!".encode())

    def set_eye_position(self, pos_id: int):
        """设置眼球位置 (1-21)，参照眼球运动图"""
        pos_id = max(1, min(21, pos_id))
        self._eye_state = pos_id
        self._conn.write(f"$DGB:{pos_id}!".encode())

    def set_eyelid(self, state: int):
        """设置眼皮状态 (1-正常, 2-眯眼, 3-闭眼, 4-瞪眼)"""
        state = max(1, min(4, state))
        self._lid_state = state
        self._conn.write(f"$DGL:{state}!".encode())

    def get_state(self) -> dict:
        """返回当前所有硬件状态"""
        return {
            "mouth": self._mouth_state,
            "eye_pos": self._eye_state,
            "eyelid": self._lid_state
        }

    def speak_start(self):
        """开始说话动画"""
        self._conn.write(b"?speak_start")

    def speak_stop(self):
        """停止说话动画"""
        self._conn.write(b"?stop")

    def close(self):
        self._conn.close()

if __name__ == "__main__":
    # --- 快速测试 ---
    print("=== RobotController 模拟测试 ===")
    robot = RobotController(mock=True)
    robot.set_mouth(3)      # 张嘴 50%
    robot.set_eye_position(5) # 看向左上
    robot.set_eyelid(2)     # 眯眼
    print(f"当前状态: {robot.get_state()}")
    robot.close()
