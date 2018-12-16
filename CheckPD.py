#!/usr/bin/env python

import urequests
import json
import bitmapfont
import machine
import utime
import network
import ht16k33_matrix
import gc


DISPLAY_WIDTH  = 16      # Display width in pixels.
DISPLAY_HEIGHT = 8       # Display height in pixels.
SPEED          = 25.0    # Scroll speed in pixels per second.

# Update to match your API key
API_KEY = ''

# Create i2c

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('', '')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())


def list_oncalls():
    gc.collect()
    url = 'https://api.pagerduty.com/oncalls'
    headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=API_KEY)
    }
    try:
        r = urequests.get(url, headers=headers)
    except Exception as e:
        gc.collect()
        print(e)
        return [('failure', 1)]
    content = r.content
    r.close()
    gc.collect()
    return [(oncall['user']['summary'], oncall['escalation_level']) for oncall in json.loads(content)['oncalls']]


def write_it(message):
    # Initialize LED matrix.
    i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))
    matrix = ht16k33_matrix.Matrix16x8(i2c)
    # Initialize font renderer using a helper function to flip the Y axis
    # when rendering so the origin is in the upper left.
    def matrix_pixel(x, y):
        matrix.pixel(x, DISPLAY_HEIGHT-1-y, 1)
    with bitmapfont.BitmapFont(DISPLAY_WIDTH, DISPLAY_HEIGHT, matrix_pixel) as bf:
        # Global state:
        pos = DISPLAY_WIDTH                 # X position of the message start.
        message_width = bf.width(message)   # Message width in pixels.
        last = utime.ticks_ms()             # Last frame millisecond tick time.
        speed_ms = SPEED / 1000.0           # Scroll speed in pixels/ms.
        # Main loop:
        count = 0
        while True:
            # Compute the time delta in milliseconds since the last frame.
            current = utime.ticks_ms()
            delta_ms = utime.ticks_diff(current, last)
            last = current
            # Compute position using speed and time delta.
            pos -= speed_ms*delta_ms
            if pos < -message_width:
                pos = DISPLAY_WIDTH
                break
            # Clear the matrix and draw the text at the current position.
            matrix.fill(0)
            bf.text(message, int(pos), 0)
            # Update the matrix LEDs.
            matrix.show()
            # Sleep a bit to give USB mass storage some processing time (quirk
            # of SAMD21 firmware right now).
            utime.sleep_ms(20)


do_connect()
while True:
    for user, level in list_oncalls():
        write_it('Level: {1} - {0}'.format(user, level))
        utime.sleep(1)
