import random
from math import sqrt
import uasyncio
from machine import ADC

IDLE = (55, 55, 0)
RX = (0, 55, 0)
TX = (0, 0, 55)
FAIL = (55, 0, 0)


class Device:
    def __init__(self, tx1_pin, tx2_pin, rx_pin, addr=None, neopixel=None):
        self.MAC_LEN = 6
        self.addr = addr
        while self.addr is None or self.addr in ['000000', '111111']:
            self.addr = ''.join(random.choice(['0', '1']) for _ in range(self.MAC_LEN))

        self.comm_tx1 = tx1_pin
        self.comm_tx2 = tx2_pin
        self.comm_rx = ADC(rx_pin)

        self.status_led = neopixel

    def frame(self, to, data):
        if not set(data) <= {'0', '1'}:
            data = str2bit(data)
        length_of_the_frame = self.MAC_LEN * 2 + 8 + len(data) + 12
        framelen_encoded = int2bit(length_of_the_frame)
        frame = ''

        frame += to
        frame += self.addr
        frame += framelen_encoded  # frame's header complete
        # frame is now '00000011111100000000'

        header_parity = generate_parity(frame)
        data_parity = generate_parity(data)

        frame += data
        # frame is now '00000011111100000000data'

        # parity calculations
        frame += header_parity + inv(header_parity)
        # frame is now '00000011111100000000data01'
        frame += data_parity
        # frame is now '00000011111100000000data010'
        frame += int2bit(0, 4)  # hops
        # frame is now '00000011111100000000data0101111'
        frame += '0' * 3
        # frame is now '00000011111100000000data0101111000'
        frame += generate_parity(frame)
        # frame is now '00000011111100000000data01011110001'
        return frame

    def unframe(self, binary):
        if len(binary) < 32 or binary is None:
            return
        if (bit2int(binary[2 * self.MAC_LEN:2 * self.MAC_LEN + 8]) * 2 + 1) == len(binary):
            binary = binary[1:]
        ret = {}
        ret['to'] = binary[0:self.MAC_LEN]
        ret['from'] = binary[self.MAC_LEN:2 * self.MAC_LEN]
        ret['framelen'] = bit2int(binary[2 * self.MAC_LEN:2 * self.MAC_LEN + 8])
        ret['data'] = binary[2 * self.MAC_LEN + 8:ret['framelen'] - 12]

        is_intact = True
        if generate_parity(binary[:-1]) != binary[-1]:
            is_intact = False
        if generate_parity(binary[0:2 * self.MAC_LEN + 8]) != binary[-10]:
            is_intact = False
        if generate_parity(ret['data']) != binary[-8]:
            is_intact = False
        ret['intact'] = is_intact

        return ret

    def is_for_me(self, binary):
        if binary[0:self.MAC_LEN] == '111111' and binary[self.MAC_LEN:2 * self.MAC_LEN] != self.addr:
            return True
        return binary[0:self.MAC_LEN] == self.addr

    def set_led(self, color):
        if self.status_led is None:
            return
        self.status_led[0] = color
        self.status_led.write()

    async def rx(self):
        buf = [0]
        value = 0
        self.set_led(RX)
        while True:
            while abs(buf[-1] - value) < 5000:  # this should wait around until the logical state changes
                value = self.comm_rx.read_u16()
            buf.append(value)
            if value < 16000 and len(buf) > 32:
                break

        queue = ''
        for raw in buf:
            if 35000 < raw < 45000:
                queue += '1'
            if 15000 < raw < 30000:
                queue += '0'
        self.set_led(IDLE)
        return queue

    async def tx(self, frame):
        self.set_led(TX)
        await self.set_logical_level(1)
        await uasyncio.sleep_ms(1)

        for bit in frame:
            await self.set_logical_level(3)
            if bit == '1':
                await self.set_logical_level(2)
            else:
                await self.set_logical_level(1)

        await self.set_logical_level(1)
        await uasyncio.sleep_ms(1)
        await self.set_logical_level(0)
        self.set_led(IDLE)
        return

    async def set_logical_level(self, value):
        if value == 0:
            self.comm_tx1.off()
            self.comm_tx2.off()
        if value == 1:
            self.comm_tx1.on()
            self.comm_tx2.off()
        if value == 2:
            self.comm_tx1.off()
            self.comm_tx2.on()
        if value == 3:
            self.comm_tx1.on()
            self.comm_tx2.on()


def generate_parity(data):
    """
    :type data str
    :param data: data to generate parity for
    :return: parity bit of the data
    """
    return '1' if data.count('1') % 2 == 1 else '0'


def inv(data):
    """
    :type data str
    :param data:
    :return: inverted binary string
    """
    return ''.join(str(1-int(i)) for i in data)


def int2bit(num, l=8):
    binary_string = bin(num)[2:]
    while len(binary_string) < l:
        binary_string = "0" + binary_string
    return binary_string


def bit2int(binary):
    return int(binary, 2)


def str2bit(string):
    return ''.join(int2bit(ord(c)) for c in string)


def bit2str(binary):
    text = ''
    for i in range(0, len(binary), 8):
        character = binary[i:i + 8]
        text += chr(int(character, 2))
    return text


print("objects library imported")
