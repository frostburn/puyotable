from itertools import permutations, chain, combinations

from gym_puyopuyo.field import TallField


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


def _canonize_field(state):
    best = bytes(state.field.data)
    for perm in permutations(range(state.num_colors)):
        trial = state.field.data[:]
        for source, target in enumerate(perm):
            for row in range(8):
                trial[8 * target + row] = state.field.data[8 * source + row]
        trial = bytes(trial)
        if trial < best:
            best = trial
    return best


def canonize_field(state):
    trial_1 = _canonize_field(state)
    state.mirror()
    trial_2 = _canonize_field(state)
    return min(trial_1, trial_2)


def _canonize_state(state):
    is_tall = isinstance(state.field, TallField)
    best = (state.deals[:], state.field.data[:])
    deals = state.deals
    field = state.field.data
    for perm in permutations(range(state.num_colors)):
        trial_deals = []
        for deal in deals:
            trial_deals.append((perm[deal[0]], perm[deal[1]]))

        trial_field = field[:]
        for source, target in enumerate(perm):
            t = 8 * target
            s = 8 * source
            for row in range(8):
                trial_field[t + row] = field[s + row]
            if is_tall:
                t += 8 * state.num_layers
                s += 8 * state.num_layers
                for row in range(8):
                    trial_field[t + row] = field[s + row]

        subtrial = trial_deals[:]
        for flips in powerset(range(len(deals))):
            for index in flips:
                c0, c1 = subtrial[index]
                subtrial[index] = (c1, c0)
            if (subtrial, trial_field) < best:
                best = (subtrial, trial_field)
    return best


def canonize_state(state):
    trial_1 = _canonize_state(state)
    state.mirror()
    trial_2 = _canonize_state(state)
    state.deals, state.field.data = min(trial_1, trial_2)
