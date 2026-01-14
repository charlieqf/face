import serial
import time

class SerialPortMock:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        print(f"[MOCK] Serial port {port} opened at {baudrate} baud (SIMULATION MODE)")

    def write(self, data):
        print(f"[MOCK SEND] {data.decode().strip()}")

    def close(self):
        print(f"[MOCK] Serial port {self.port} closed.")

# 在没有硬件时，可以使用这个类代替真实的 serial.Serial
