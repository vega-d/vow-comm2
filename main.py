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

me.listener_add(objects.Listener('.*', on_met=print))  # accept anything and print

async def loop():
    await me.tx(me.frame('*', 'test'))  # send a broadcast test packet
    me.listener_run()  # run all the listeners


    await uasyncio.sleep_ms(500)


while True:
    uasyncio.run(loop())
