# A collection of utilites for the Feather M4 for EE11SC

import board
import busio
import sdcardio
import storage
import os

# mount the sd card on a Feather M4, assuming the chip select is D4
def mount_sd():

    # set up the SPI bus, and use D4 for chip select
    spi = board.SPI()
    cs = board.D4

    # open the card up, and mount it as a file system
    sdcard = sdcardio.SDCard(spi,cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs,"/sd")
    return

# a utility to print a file
def print_file(fn):
    with open(fn,"r") as f:
        for line in f:
            print(line,end='')
    return

# Scan the I2C bus, and report the hex addresses of the devices it finds
def scan_i2c():

    # set up I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # we have to lock the bus before we can scan it
    i2c.try_lock()

    # Print what we find in hex
    print([hex(x) for x in i2c.scan()])

    # unlock bus in case someone else wants to use it
    i2c.unlock()
    i2c.deinit()
    return