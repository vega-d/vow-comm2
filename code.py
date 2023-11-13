from cmath import sqrt

print("vow-comm2 init")
import neopixel
from machine import Pin, ADC
import objects
import uasyncio

IDLE = (255, 255, 0)
RX = (0, 255, 0)
TX = (0, 0, 255)
FAIL = (255, 0, 0)
status_led = neopixel.NeoPixel(Pin(16), 1)


def set_led(color):
    status_led[0] = color
    status_led.write()


print("vow-comm2 device init started")
me = objects.Device()
set_led(IDLE)
history = [0 for _ in range(50)]
print("vow-comm2 device init finished, device addr:", me.addr)

comm_tx1 = Pin(14, Pin.OUT)
comm_tx2 = Pin(3, Pin.OUT)
comm_rx = ADC(Pin(28))


def avg(array):
    return sum(array) // len(array)


def delta(array):
    ret = [0 for _ in array]
    for i in range(1, len(array)):
        ret[i - 1] = array[i] - array[i - 1]
    return ret


def debounce(value):
    global history

    history.append(value)
    if len(history) > 50:
        history.pop(1)

    if avg(delta(history[1:20])) > avg(delta(history[30:])):
        history[0] = history[25]

    return history[0]


async def rx():
    buf = [0]
    value = 0
    while True:
        while abs(buf[-1] - value) < 5000:  # this should wait around until the logical state changes
            value = comm_rx.read_u16()
        buf.append(value)
        if value < 16000 and len(buf) > 32:
            break

    queue = ''
    for raw in buf:
        if 35000 < raw < 45000:
            queue += '1'
        if 15000 < raw < 30000:
            queue += '0'
    return queue


async def dac_simplify(value):
    global comm_tx1
    global comm_tx2
    if value == 0:
        comm_tx1.off()
        comm_tx2.off()
    if value == 1:
        comm_tx1.on()
        comm_tx2.off()
    if value == 2:
        comm_tx1.off()
        comm_tx2.on()
    if value == 3:
        comm_tx1.on()
        comm_tx2.on()


async def tx(frame):
    set_led(TX)
    print("tx:", frame)

    start_seq = '---'
    for bit in start_seq:
        if bit == '-':
            await dac_simplify(2)
        if bit == '0':
            await dac_simplify(1)
        else:
            await dac_simplify(3)

    for bit in frame:
        await dac_simplify(3)
        if bit == '1':
            await dac_simplify(2)
        else:
            await dac_simplify(1)

    await dac_simplify(0)
    await uasyncio.sleep_ms(1)
    set_led(IDLE)
    return


async def main():
    global comm_rx
    global comm_tx
    # uasyncio.run(
    #     tx(me.frame('111111', 'hello')))  # launch a new instance of tx when we want to transmit something

    queue_rx = uasyncio.run(rx())[1:]
    print("frame:", queue_rx, '; len:', len(queue_rx))
    if me.unframe(queue_rx) is not None:
        print(objects.bit2str(me.unframe(queue_rx)['data']), end='; ')
        print((me.unframe(queue_rx)['intact']), end='; ')
        print((me.unframe(queue_rx)['framelen']))
    await uasyncio.sleep_ms(5)
