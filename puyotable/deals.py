from itertools import permutations, chain, combinations


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def canonize_deals(deals, num_colors):
    best = tuple(deals)
    for perm in permutations(range(num_colors)):
        trial = []
        for deal in deals:
            trial.append((perm[deal[0]], perm[deal[1]]))
        subtrial = trial[:]
        for flips in powerset(range(len(deals))):
            for index in flips:
                c0, c1 = subtrial[index]
                subtrial[index] = (c1, c0)
            if tuple(subtrial) < best:
                best = tuple(subtrial)
    return best
