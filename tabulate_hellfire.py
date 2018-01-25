from __future__ import division

import argparse
import json

from gym_puyopuyo.state import State

from puyotable.compress import num_encode
# from puyotable.field import canonize_field
from tabulate_deals import unique_deals

import puyocore as core


def canonize_field_light(state):
    data = bytes(state.field.data)
    state.mirror()
    mirrored_data = bytes(state.field.data)
    return min(data, mirrored_data)


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
        state.width,
        state.tsu_rules,
        state.has_garbage,
        action_mask,
        colors,
        depth,
        factor,
    ]
    return core.tall_tree_search(*search_args)

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
        'width', metavar='width', type=int,
        help='How wide a board to use'
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
        base_state = State(13, args.width, args.num_colors, deals=deals, tsu_rules=True)
        # base_state.render()

        search_space = set()
        def collect(state):
            if len(state.deals) >= args.num_deals:
                for child, reward in state.get_children():
                    collect(child)
            else:
                search_space.add(canonize_field_light(state))

        collect(base_state)

        print("Collected", len(search_space), "states")

        print("Doing the searches")

        state = base_state.clone()
        state.deals = base_state.deals[args.surface_depth + 1:]
        for field_data in search_space:
            state.field.data = bytearray(field_data)
            score = tree_search(state, args.depth)
            state.render()
            print(score)
            encoded = num_encode(state.field_to_int())
            prefix = []
            for deal in state.deals:
                prefix.extend(deal)
            prefix = "".join(map(str, prefix))
            key = "{}{}".format(prefix, encoded)
            values[key] = score

        print("Collected", len(values), "values so far")

    if args.outfile:
        data = {
            "metadata": {
                "num_colors": args.num_colors,
                "surface_depth": args.surface_depth,
                "depth": args.depth,
                "width": args.width,
                "num_deals": args.num_deals,
            },
            "scores": values,
        }
        with open(args.outfile, "w") as f:
            json.dump(data, f)
        print("Saved result to", args.outfile)
