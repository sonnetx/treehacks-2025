import serial
import time

ser = serial.Serial('/dev/tty.usbmodem1101', 115200, timeout=1)

def show_correct():
    ser.write(f"correct\n".encode())
    print(f"Sent command: correct")

def show_incorrect():
    ser.write(f"incorrect\n".encode())
    print(f"Sent command: incorrect")

show_correct()
ser.close()


