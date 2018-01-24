from puyotable.deals import canonize_deals


def test_canonize():
    deals = [(1, 2), (0, 1)]
    canonized = canonize_deals(deals, 3)
    print(canonized)
    assert (canonized <= tuple(deals))
