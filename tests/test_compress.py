import json

from puyotable.compress import num_encode, num_decode


def test_encoding():
    for i in range(1000):
        encoded = num_encode(i)
        assert (json.dumps(encoded).strip('"') == encoded)
        assert (i == num_decode(encoded))
