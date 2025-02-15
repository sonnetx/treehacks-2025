import time
import board
import displayio
import digitalio
from adafruit_pyportal import PyPortal
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label
import terminalio
import random
from adafruit_debouncer import Debouncer
import adafruit_rfm9x
import busio

# LORA connection to glove
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.SD_CS)
reset = digitalio.DigitalInOut(board.D4)
rfm9x = adafruit_rfm9x.RFM9x(
    spi=spi, cs=cs, reset=reset, frequency=915.0, baudrate=1000000
)

display = board.DISPLAY
display.rotation = 90
main_group = displayio.Group()