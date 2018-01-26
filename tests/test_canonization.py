import random

from gym_puyopuyo.state import State
import pytest

from puyotable.canonization import canonize_deals, canonize_state


def test_canonize_deals():
    deals = [(1, 2), (0, 1)]
    canonized = canonize_deals(deals, 3)
    print(canonized)
    assert (canonized <= tuple(deals))


@pytest.mark.parametrize("height", [8, 16])
def test_canonize_state(height):
    state = State(height, 5, 4, 4)

    for _ in range(35):
        state.step(*random.choice(state.actions))

    state.num_deals = None
    state.render()

    canonize_state(state)

    state.render()

    # TODO: Actually test for something
