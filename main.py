from cmath import sqrt

print("vow-comm2 init")
import neopixel
from machine import Pin, ADC
import objects
import uasyncio

print("vow-comm2 device init started")
me = objects.Device(Pin(2, Pin.OUT), Pin(3, Pin.OUT), Pin(28), 'rp2040', neopixel=neopixel.NeoPixel(Pin(16), 1))
me.set_led(objects.IDLE)
print("vow-comm2 device init finished, device addr:", me.addr)


async def main():

    await uasyncio.sleep_ms(500)


while True:
    uasyncio.run(main())
