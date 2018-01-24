import argparse
from collections import Counter
import json

from gym_puyopuyo.state import State

from tabulate_deals import unique_deals
from puyotable.compress import num_encode


def state_key(state):
    data = bytes(state.field.data)
    state.mirror()
    mirrored_data = bytes(state.field.data)
    return (min(data, mirrored_data), len(state.deals))


def state_from_key(base_state, key):
    data, depth = key
    state = base_state.clone()
    state.field.data[:] = data
    if not depth:
        state.deals = []
    else:
        state.deals = base_state.deals[-depth:]
    return state


def can_clear(state, values):
    key = state_key(state)
    if values[key] is not None:
        return values[key]
    for child, score in state.get_children():
        if not any(child.field.data):
            return True
        if can_clear(child, values):
            return True
    return False


def deals_have_potential(deals):
    counts = Counter()
    for deal in deals:
        counts[deal[0]] += 1
        counts[deal[1]] += 1
        if all(v >= 4 for v in counts.values()):
            return True
    return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Tabulate all openings in Puyo Puyo.'
    )
    parser.add_argument(
        'num_colors', metavar='colors', type=int,
        help='Number of available colors'
    )
    parser.add_argument(
        'depth', metavar='depth', type=int,
        help='How many pieces deep to tabulate'
    )
    parser.add_argument(
        'width', metavar='width', type=int,
        help='How wide a board to use'
    )
    parser.add_argument(
        '--infile', metavar='f', type=str,
        help='Filename for precalculated opening sequence data'
    )
    parser.add_argument(
        '--outfile', metavar='f', type=str,
        help='Filename for JSON output'
    )

    args = parser.parse_args()

    if args.infile:
        print("Loading deals from {}".format(args.infile))
        with open(args.infile) as f:
            dealss = json.load(f)
    else:
        print("Recalculating deals")
        dealss = unique_deals(args.depth, args.num_colors)
    print("Processing {} unique sequences".format(len(dealss)))

    result = []

    for deals in dealss:
        if not deals_have_potential(deals):
            print("Provably cannot clear", deals)
            continue

        base_state = State(8, args.width, args.num_colors, deals=deals)
        base_state.render()

        values = {}

        def collect(state):
            key = state_key(state)
            if key in values:
                return
            values[key] = None
            for child, reward in state.get_children():
                collect(child)

        collect(base_state)
        print("Number of unique positions", len(values))

        for depth in range(len(base_state.deals) + 1):
            # print("Searching depth =", depth)
            for key in values:
                if key[1] == depth:
                    state = state_from_key(base_state, key)
                    values[key] = can_clear(state, values)
        print("Can clear?", values[state_key(base_state)])

        subresult = []
        for key, value in values.items():
            if not value:
                continue
            depth = key[1]
            state = state_from_key(base_state, key)
            encoded = num_encode(state.field_to_int())
            subresult.append('{}{}'.format(encoded, depth))
        result.append(subresult)

    if args.outfile:
        data = {
            "metadata": {
                "num_colors": args.num_colors,
                "depth": args.depth,
                "width": args.width,
                "deals": sorted(dealss),
            },
            "all_clears": result,
        }
        with open(args.outfile, "w") as f:
            json.dump(data, f)
        print("Saved result to", args.outfile)
