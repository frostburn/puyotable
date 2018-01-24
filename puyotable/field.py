from itertools import permutations


def _canonize_field(state):
    best = bytes(state.field.data)
    for perm in permutations(range(state.num_colors)):
        trial = state.field.data[:]
        for source, target in enumerate(perm):
            trial[target] = state.field.data[source]
        trial = bytes(trial)
        if trial < best:
            best = trial
    return best


def canonize_field(state):
    trial_1 = _canonize_field(state)
    state.mirror()
    trial_2 = _canonize_field(state)
    return min(trial_1, trial_2)
