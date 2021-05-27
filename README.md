# CoapTesting

> A simple series of Python3 functions to test the performance of a CoAP server using libcoap.

## About

This project is a Python wrapper for the `coap-client` command providing various testing utilities.

## Dependencies

As this project utilises the `coap-client` command, [libcoap](https://github.com/obgm/libcoap) must be installed and
the `coap-client` must be present within the users PATH.

More Details: <https://github.com/obgm/libcoap>

## Usage

The `coap.py` module contains various different utility functions. Examples of usage can be seen below. In the future
this project may produce an official pip package, but for now `coap.py` must be copied into your projects structure.

```python3
from coap import *

addr = '192.168.1.12'

time, res = test(GET, 'temp', addr)

_, _ = test(PUT, 'temp', 'VALUE')
_ = test_paths(GET, ['temp', 'humid'], addr)
_ = test_times_sync(GET, 'temp', addr, 100)
_ = test_times_multi(GET, 'temp', addr, 100, workers=10)
```