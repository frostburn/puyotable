from __future__ import division

import argparse
import json

from gym_puyopuyo.state import State

from puyotable.compress import num_encode
from puyotable.field import canonize_field
from tabulate_deals import unique_deals


GAMMA = 0.9
DEATH_VALUE = -1000


def does_clear(state):
    for child in state.get_children():
        if not any(child.field.data):
            return True
    return False


def tree_search(state, depth, heuristic):
    if depth <= 0:
        return 0

    if state.deals:
        return _tree_search_single(state, depth, heuristic)
    tree_score = 0
    clone = state.clone()
    for c0 in range(state.num_colors):
        # Symmetry reduction
        for c1 in range(c0, state.num_colors):
            clone.deals = [(c0, c1)]
            single_score = _tree_search_single(clone, depth, heuristic)
            # Symmetry compensation
            if c0 == c1:
                tree_score += single_score
            else:
                tree_score += 2 * single_score
    tree_score /= state.num_colors ** 2
    return tree_score


def _tree_search_single(state, depth, heuristic):
    score = DEATH_VALUE
    for child, move_score in state.get_children():
        # Replace chain score with all clear game over
        if not any(child.field.data):
            child_score = 1
        else:
            tree_score = tree_search(child, depth -1, heuristic)
            child_score = 0 * move_score + GAMMA * tree_score
        if child_score > score:
            score = child_score
    return score


if __name__ == "__main__":
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


    leaves = set()
    def collect(state):
        if state.deals:
            for child, reward in state.get_children():
                collect(child)
        else:
            leaves.add(canonize_field(state))

    for deals in dealss:
        # if not deals_have_potential(deals):
        #     print("Provably cannot clear", deals)
        #     continue

        base_state = State(8, args.width, args.num_colors, deals=deals)
        base_state.render()

        collect(base_state)

        print("Collected", len(leaves), "leaves so far")


    print("Doing the searches")

    values = {}
    state = base_state.clone()
    state.deals = []
    for field_data in leaves:
        state.field.data = bytearray(field_data)
        chance = tree_search(state, 1, None)
        encoded = num_encode(state.field_to_int())
        values[encoded] = chance

    print("Collected", len(values), "values")

    if args.outfile:
        data = {
            "metadata": {
                "num_colors": args.num_colors,
                "depth": args.depth,
                "width": args.width,
            },
            "all_clear_chances": values,
        }
        with open(args.outfile, "w") as f:
            json.dump(data, f)
        print("Saved result to", args.outfile)
