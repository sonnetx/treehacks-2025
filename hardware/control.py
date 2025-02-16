import serial
import time

# Replace 'COM3' with the appropriate port for your Feather
ser = serial.Serial('COM3', 115200, timeout=1)


def send_command(command):
    ser.write(f"{command}\n".encode())
    print(f"Sent command: {command}")


try:
    while True:
        command = input("Enter command (correct/incorrect): ").strip().lower()
        if command in ['correct', 'incorrect']:
            send_command(command)
        elif command == 'exit':
            break
        else:
            print("Invalid command. Use 'correct' or 'incorrect'.")
finally:
    ser.close()
