# vow-comm2 - Vega's One Wire communication protocol

Why did I make this? Don't ask me. Please do not use this in a serious project.

This is a relatively simple micropython library that allows to use a pair of digital out pins and a analog-to-digital input pin for network communication.
It needs less wires than I2C or SPI, but unlike UART it can support multiple devices on the same bus.

A frame sent out with this library is composed of header, encapsulated data and a parity block.

The header is 20 bits long: 
- 6 bits of where the frame is intended to arrive
- 6 bits of where the packet originated
- 8 bits encoding the total length of the frame

The encapsulated data has to be a UTF-8 encoded string 