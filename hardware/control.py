import serial
import time

ser = serial.Serial('/dev/cu.usbmodem2101', 115200, timeout=1)

def show_correct():
    ser.write(f"correct\n".encode())
    print(f"Sent command: correct")

def show_incorrect():
    ser.write(f"incorrect\n".encode())
    print(f"Sent command: incorrect")

ser.close()
