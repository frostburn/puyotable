import json
import random

from gym_puyopuyo.state import State
import pytest

from puyotable.compress import num_encode, num_decode, state_encode, state_decode


def test_encoding():
    for i in range(1000):
        encoded = num_encode(i)
        assert (json.dumps(encoded).strip('"') == encoded)
        assert (i == num_decode(encoded))


@pytest.mark.parametrize("height", [8, 16])
def test_state_encoding(height):
    state = State(height, 5, 4, 4)

    for _ in range(25):
        state.step(*random.choice(state.actions))

    state.num_deals = None
    state.render()

    deals = state.deals[:]
    field = state.field.to_list()
    encoded = state_encode(state)
    print(encoded)

    state.field.reset()
    state.deals = []
    decoded = state_decode(state, encoded)
    decoded.render()

    assert (deals == decoded.deals)
    assert (field == decoded.field.to_list())
