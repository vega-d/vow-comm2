from cmath import sqrt

print("vow-comm2 init")
import neopixel
from machine import Pin, ADC
import objects
import uasyncio


print("vow-comm2 device init started")
me = objects.Device(Pin(2, Pin.OUT), Pin(3, Pin.OUT), Pin(28), neopixel=neopixel.NeoPixel(Pin(16), 1))
me.set_led(objects.IDLE)
print("vow-comm2 device init finished, device addr:", me.addr)


async def main():
    await me.tx(me.frame('111111', 'hello'))

    queue_rx = uasyncio.run(me.rx())
    print("frame:", queue_rx, '; len:', len(queue_rx))
    data = me.unframe(queue_rx)
    if data is not None:
        print(objects.bit2str(data['data']), end='; ')
        print(data['intact'], end='; ')
        print(data['framelen'])
    await uasyncio.sleep_ms(500)
