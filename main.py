# 项目入口文件
# 
# 运行方式 (Usage):
# 1. 激活虚拟环境: .\venv\Scripts\activate
# 2. 启动程序: python main.py
# 
# 注意: Mock 模式开关在 config.yaml 中配置

from src.hardware.serial_port import SerialPortMock

def main():
    print("Initializing Robot Head System...")
    # 示例启动逻辑
    ser = SerialPortMock("COM3", 9600)
    ser.write(b"#DGM:1!")
    print("System Ready.")

if __name__ == "__main__":
    main()
