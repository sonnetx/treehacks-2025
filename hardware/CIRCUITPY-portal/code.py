import time
import board
import busio
import displayio
import terminalio
import digitalio
import audiocore
import audioio
import adafruit_rfm9x
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label

# Initialize Display
display = board.DISPLAY
display.rotation = 0

# Initialize LoRa Module
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.SD_CS)
reset = digitalio.DigitalInOut(board.D4)
rfm9x = adafruit_rfm9x.RFM9x(
    spi=spi, cs=cs, reset=reset, frequency=915.0, baudrate=1000000
)

# Audio Setup
speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
speaker_enable.direction = digitalio.Direction.OUTPUT
speaker_enable.value = True  # Enable speaker
audio = audioio.AudioOut(board.SPEAKER)

# Screen Dimensions
HEIGHT = 320
WIDTH = 480

# Sound Files
soundIncorrect = "error.wav"
soundCorrect = "ding.wav"

# Play Sound


def play_sound(filename):
    try:
        with open(filename, "rb") as file:
            wave = audiocore.WaveFile(file)
            audio.play(wave)
            while audio.playing:
                pass
    except OSError:
        print(f"Sound file {filename} not found!")


# Correct Screen
correct_group = displayio.Group()
block = Rect(0, 0, WIDTH, HEIGHT, fill=0x00F000)
text = label.Label(
    terminalio.FONT,
    text="Correct!",
    color=0x000000,
    scale=5,
    anchor_point=(0.5, 0.5),
    anchored_position=(WIDTH // 2, HEIGHT // 2),
)
correct_group.append(block)
correct_group.append(text)

# Incorrect Screen
incorrect_group = displayio.Group()
block = Rect(0, 0, WIDTH, HEIGHT, fill=0xF00000)
text = label.Label(
    terminalio.FONT,
    text="Incorrect!",
    color=0x000000,
    scale=5,
    anchor_point=(0.5, 0.5),
    anchored_position=(WIDTH // 2, HEIGHT // 2),
)
incorrect_group.append(block)
incorrect_group.append(text)

# Black Screen (Default)
black_screen = displayio.Group()
black_rect = Rect(0, 0, WIDTH, HEIGHT, fill=0x000000)
black_screen.append(black_rect)

display.root_group = black_screen  # Start with a black screen


def show_correct():
    print("Displaying Correct!")
    display.root_group = correct_group
    play_sound(soundCorrect)
    time.sleep(5)
    display.root_group = black_screen


def show_incorrect():
    print("Displaying Incorrect!")
    display.root_group = incorrect_group
    play_sound(soundIncorrect)
    time.sleep(5)
    display.root_group = black_screen


print("Listening for LoRa messages...")

# LoRa Receiver Loop
while True:
    packet = rfm9x.receive()
    if packet:
        message = packet.decode("utf-8").strip()  # Decode received message
        print(f"Received: {message}")

        if message == "correct":
            show_correct()
        elif message == "incorrect":
            show_incorrect()