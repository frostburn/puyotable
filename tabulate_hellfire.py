from __future__ import division

import argparse
import json

from gym_puyopuyo.state import State
from gym_puyopuyo.field import TallField

from puyotable.compress import state_encode, state_decode
from puyotable.canonization import canonize_state
from tabulate_deals import unique_deals

import puyocore as core


def tree_search(state, depth, factor=1e-5):
    colors = []
    for deal in state.deals:
        colors.extend(deal)

    action_mask = 0
    for action in state.actions:
        action_mask |= 1 << state._validation_actions.index(action)

    search_args = [
        state.field.data,
        state.num_layers,
        state.has_garbage,
        action_mask,
        colors,
        depth,
        factor,
    ]
    search_fun = core.bottom_tree_search
    if isinstance(state.field, TallField):
        search_args.insert(2, state.tsu_rules)
        search_args.insert(2, state.width)
        search_fun = core.tall_tree_search

    return search_fun(*search_args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Tabulate hellfire style opener values in Puyo Puyo.'
    )
    parser.add_argument(
        'num_colors', metavar='colors', type=int,
        help='Number of available colors'
    )
    parser.add_argument(
        'surface_depth', metavar='surface_depth', type=int,
        help='How deep to start tabulating'
    )
    parser.add_argument(
        'depth', metavar='depth', type=int,
        help='How many pieces deep to tabulate'
    )
    parser.add_argument(
        '--width', metavar='width', type=int, default=6,
        help='How wide a board to use'
    )
    parser.add_argument(
        '--height', metavar='height', type=int, default=13,
        help='How high a board to use'
    )
    parser.add_argument(
        '--num_deals', metavar='n', type=int, default=3,
        help='How many pieces are shown during play'
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

    deals_depth = args.surface_depth + args.num_deals

    if args.infile:
        print("Loading deals from {}".format(args.infile))
        with open(args.infile) as f:
            dealss = json.load(f)
    else:
        print("Recalculating deals")
        dealss = unique_deals(deals_depth, args.num_colors)
    print("Processing {} unique sequences".format(len(dealss)))

    values = {}
    for deals in dealss:
        base_state = State(args.height, args.width, args.num_colors, deals=deals, tsu_rules=(args.height == 13))
        # base_state.render()

        def collect(state):
            if len(state.deals) >= args.num_deals:
                for child, reward in state.get_children():
                    collect(child)
            else:
                canonize_state(state)
                values[state_encode(state)] = None

        collect(base_state)

    print("Collected", len(values), "states")

    print("Doing the searches...")

    for encoded in values.keys():
        state = state_decode(base_state, encoded)
        score = tree_search(state, args.depth)
        state.render()
        print(score)
        values[encoded] = score

    print("Collected", len(values), "values")

    if args.outfile:
        data = {
            "metadata": {
                "num_colors": args.num_colors,
                "surface_depth": args.surface_depth,
                "depth": args.depth,
                "width": args.width,
                "height": args.height,
                "num_deals": args.num_deals,
            },
            "scores": values,
        }
        with open(args.outfile, "w") as f:
            json.dump(data, f)
        print("Saved result to", args.outfile)
