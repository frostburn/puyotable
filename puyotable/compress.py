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
