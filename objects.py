import random
from math import sqrt


class Device:
    def __init__(self, addr=None):
        self.MAC_LEN = 6
        self.addr = addr
        while self.addr is None or self.addr == '000000':
            self.addr = ''.join(random.choice(['0', '1']) for _ in range(self.MAC_LEN))

    def frame(self, to, data):
        if not set(data) <= {'0', '1'}:
            data = str2bit(data)
        length_of_the_frame = self.MAC_LEN * 2 + 8 + len(data) + 12
        framelen_encoded = int2bit(length_of_the_frame)
        frame = ''

        frame += to
        frame += self.addr
        frame += framelen_encoded  # frame's header complete

        header_parity = generate_parity(frame)
        data_parity = generate_parity(data)

        frame += data

        # parity calculations
        frame += header_parity + inv(header_parity)
        frame += data_parity
        frame += int2bit(0, 4)  # hops
        frame += '0' * 3
        frame += generate_parity(frame)

        return frame

    def unframe(self, binary):
        if len(binary) < 32:
            return
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
        if binary[0:self.MAC_LEN] == '000000' and binary[self.MAC_LEN:2 * self.MAC_LEN] != self.addr:
            return True
        return binary[0:self.MAC_LEN] == self.addr


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
    data = data.replace('1', '2')
    data = data.replace('0', '1')
    data = data.replace('2', '0')

    return data


def int2bit(num, l=8):
    binary_string = bin(num)[2:]
    while len(binary_string) < l:
        binary_string = "0" + binary_string
    return binary_string


def bit2int(binary):
    return int(binary, 2)


def str2bit(string):
    binary_string = ''

    for c in string:
        binary_string += int2bit(ord(c))
    return binary_string


def bit2str(binary):
    text = ''
    for i in range(0, len(binary), 8):
        character = binary[i:i + 8]
        text += chr(int(character, 2))
    return text


print("objects library imported")
