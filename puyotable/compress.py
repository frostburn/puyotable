# ASCII printable characters except whitespace, quotes or backslash.
ALPHABET = (
    '!#$%&()*+,-./'
    '0123456789'
    ':;<=>?@'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '[]^_`'
    'abcdefghijklmnopqrstuvwxyz'
    '{|}~'
)
ALPHABET_REVERSE = dict((c, i) for (i, c) in enumerate(ALPHABET))
BASE = len(ALPHABET)


def num_encode(n):
    if n < 0:
        raise ValueError('Cannot encode negative numbers')
    s = []
    while True:
        n, r = divmod(n, BASE)
        s.append(ALPHABET[r])
        if n == 0:
            break
    return ''.join(reversed(s))


def num_decode(s):
    n = 0
    for c in s:
        n = n * BASE + ALPHABET_REVERSE[c]
    return n


def state_encode(state):
    n = state.field_to_int()
    flat = []
    for deal in state.deals:
        flat.extend(deal)
    flat = ''.join(map(str, flat))
    return '{}|{}'.format(num_encode(n), flat)


def state_decode(base_state, s):
    state = base_state.clone()
    s, flat = s.rsplit('|', 1)
    flat = list(map(int, flat))
    deals = []
    while flat:
        deals.append((flat.pop(0), flat.pop(0)))
    state.deals = deals
    n = num_decode(s)
    state.field_from_int(n)
    return state
