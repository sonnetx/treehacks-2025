# FEATHER
import adafruit_rfm9x
import busio
import board
import time
import digitalio
from adafruit_debouncer import Debouncer

# LORA SETUP
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D9)
reset = digitalio.DigitalInOut(board.D10)
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0, baudrate=1000000)

# BUTTON SETUP
pin_correct = digitalio.DigitalInOut(board.D6)
pin_correct.direction = digitalio.Direction.INPUT
pin_correct.pull = digitalio.Pull.UP
button_correct = Debouncer(pin_correct)

pin_incorrect = digitalio.DigitalInOut(board.D5)
pin_incorrect.direction = digitalio.Direction.INPUT
pin_incorrect.pull = digitalio.Pull.UP
button_incorrect = Debouncer(pin_incorrect)


def send_correct():
    print("Sending: Correct")
    rfm9x.send("correct")


def send_incorrect():
    print("Sending: Incorrect")
    rfm9x.send("incorrect")


print("Initialized!")

while True:
    button_correct.update()
    button_incorrect.update()

    if button_correct.fell:
        send_correct()

    if button_incorrect.fell:
        send_incorrect()
