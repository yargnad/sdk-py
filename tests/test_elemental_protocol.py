import struct


def normalize_elemental(bytes4):
    earth, air, water, fire = struct.unpack('<bbbb', bytes4)
    return [earth/127.0, air/127.0, water/127.0, fire/127.0]


def test_normalize_elemental():
    b = struct.pack('<bbbb', 127, -127, 0, 64)
    vals = normalize_elemental(b)
    assert vals[0] == 1.0
    assert round(vals[1], 3) == -1.0
    assert vals[2] == 0.0
    assert round(vals[3], 3) == 0.504
