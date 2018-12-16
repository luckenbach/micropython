import machine
import time
import ht16k33_matrix

i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))
matrix = ht16k33_matrix.Matrix16x8(i2c)


while True:
    matrix.fill(False)
    for x in range(0,15):
        top = randrange(1,7)
        for y in range(0,top):
            matrix.pixel(x,y,True)
    matrix.show()
    time.sleep(0.25)
