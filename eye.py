import array
import neopixel as neopixel
import rp2
from machine import Pin, PWM, ADC
import uasyncio

print("imported eye")

IDLE = (255, 255, 0)
RX = (0, 255, 0)
TX = (0, 0, 255)
FAIL = (255, 0, 0)

status_led = neopixel.NeoPixel(Pin(16), 1)


def set_led(color):
    status_led[0] = color
    status_led.write()


comm_txs = Pin(14)
comm_tx = Pin(3)
comm_rx = ADC(Pin(28))


@rp2.asm_pio(sideset_init=rp2.PIO.OUT_HIGH, out_init=rp2.PIO.OUT_HIGH, out_shiftdir=rp2.PIO.SHIFT_RIGHT, fifo_join=rp2.PIO.JOIN_TX)
def asm_tx():
    # Block with TX deasserted until data available
    pull()
    # Initialise bit counter, assert start bit for 8 cycles
    set(x, 1)  .side(0)       [7]
    # Shift out 8 data bits, 8 execution cycles per bit
    label("bitloop")
    out(pins, 8) [7] # at it's limit!
    jmp(x_dec, "bitloop")


@rp2.asm_pio(sideset_init=rp2.PIO.IN_LOW, fifo_join=rp2.PIO.JOIN_RX, out_shiftdir=0, autopush=True, push_thresh=8)
def asm_rx():
    # Shift out 8 data bits, 8 execution cycles per bit
    wait(1, pin, rel(0))
    set(x, 7)
    label("bitloop")
    in_(pins, 1)
    jmp(x_dec, "bitloop")



async def eye_test_tx():
    global comm_tx
    global comm_txs

    sm = rp2.StateMachine(0, asm_tx, freq=1_000_000, sideset_base=comm_tx, out_base=comm_tx)
    sm.active(1)
    print('activated state machine')
    # Output an array of booleans to pin 4 consecutively
    is_on = array.array('B', [True, False, True, True, True, False, False, True])
    sm.active(1)

    while True:
        while sm.tx_fifo():
            await uasyncio.sleep_ms(1)
        sm.put(is_on)
        await uasyncio.sleep_ms(3)
        # print('finished putting data into the state machine')



history = [0]


async def eye_test_rx(speed=3):
    global comm_rx
    buf = [0]
    value = 0
    while True:
        while abs(buf[-1] - value) < 5000: # this should wait around until the logical state changes
            value = comm_rx.read_u16()
        buf.append(value)
        buf.append(value)
        if value < 16000 and len(buf) > 32:
            break
    print('\n'.join(str(i) for i in buf))


def rx():
    uasyncio.run(eye_test_rx())


def tx():
    print('starting eye tx')
    uasyncio.run(eye_test_tx())
