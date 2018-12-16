# Random number range generator lifted from 
# https://github.com/adafruit/micropython-adafruit-gfx/blob/master/examples/ili9341_randlines.py

def randrange(min_value, max_value):
    # Simple randrange implementation for ESP8266 uos.urandom function.
    # Returns a random integer in the range min to max.  Supports only 32-bit
    # int values at most.
    magnitude = abs(max_value - min_value)
    randbytes = uos.urandom(4)
    offset = int((randbytes[3] << 24) | (randbytes[2] << 16) | (randbytes[1] << 8) | randbytes[0])
    offset %= (magnitude+1)  # Offset by one to allow max_value to be included.
    return min_value + offset
