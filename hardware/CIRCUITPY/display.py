import time
import board
import displayio
import terminalio
from adafruit_pyportal import PyPortal
from adafruit_display_shapes.rect import Rect
from adafruit_display_text import label

# Initialize PyPortal
pyportal = PyPortal(default_bg=None)
display = board.DISPLAY
display.rotation = 0

HEIGHT = 320
WIDTH = 480
soundIncorrect = '/error.wav'
soundCorrect = '/ding.wav'

# CORRECT
correct_group = displayio.Group()
block = Rect(0, 0, WIDTH, HEIGHT, fill=0x00F000)
text = label.Label(
    terminalio.FONT,
    text="Correct!",
    color=0x000000,
    scale=5,
    anchor_point=(0.5, 0.5),
    anchored_position=(WIDTH // 2, HEIGHT // 2)
)
correct_group.append(block)
correct_group.append(text)

# INCORRECT
incorrect_group = displayio.Group()
block = Rect(0, 0, WIDTH, HEIGHT, fill=0xF00000)
text = label.Label(
    terminalio.FONT,
    text="Incorrect!",
    color=0x000000,
    scale=5,
    anchor_point=(0.5, 0.5),
    anchored_position=(WIDTH // 2, HEIGHT // 2)
)
incorrect_group.append(block)
incorrect_group.append(text)

# BLACK SCREEN
black_screen = displayio.Group()
black_rect = Rect(0, 0, WIDTH, HEIGHT, fill=0x000000)
black_screen.append(black_rect)

def show_correct():
    print("Displaying Correct!")
    display.root_group = correct_group
    pyportal.play_file(soundCorrect)
    time.sleep(5)
    display.root_group = black_screen

def show_incorrect():
    print("Displaying Incorrect!")
    display.root_group = incorrect_group
    pyportal.play_file(soundIncorrect)
    time.sleep(5)
    display.root_group = black_screen 
