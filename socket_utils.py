#!/usr/bin/env python3
# Documentation: https://docs.python.org/3/library/struct.html
import json
import struct


def send_json(socket, json_string):
    data = json_string.encode("utf-8")
    json_length = struct.pack("!i", len(data))
    socket.sendall(json_length)
    socket.sendall(data)


def recv_json(socket):
    buffer = socket.recv(4)
    json_length = struct.unpack("!i", buffer)[0]

    # Reference: https://stackoverflow.com/a/15964489/9798310
    buffer = bytearray(json_length)
    view = memoryview(buffer)
    while json_length:
        n_bytes = socket.recv_into(view, json_length)
        view = view[n_bytes:]
        json_length -= n_bytes

    json_string = buffer.decode("utf-8")
    return json.loads(json_string)
