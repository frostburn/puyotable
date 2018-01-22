import argparse
import json

from puyotable.deals import canonize_deals


def all_deals(num_deals, num_colors):
    if not num_deals:
        return [[]]
    result = []
    for c0 in range(num_colors):
        for c1 in range(num_colors):
            for deals in all_deals(num_deals - 1, num_colors):
                result.append(deals + [(c0, c1)])
    return result


def for_all_deals(num_deals, num_colors, callback, prefix=[]):
    if not num_deals:
        callback(prefix)
        return
    for c0 in range(num_colors):
        for c1 in range(num_colors):
            for_all_deals(
                num_deals - 1,
                num_colors,
                callback,
                prefix + [(c0, c1)]
            )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Tabulate all opening sequences in Puyo Puyo.'
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
        '--outfile', metavar='f', type=str,
        help='Filename for JSON output'
    )

    args = parser.parse_args()

    canonized = set()

    def callback(deals):
        canonized.add(canonize_deals(deals, args.num_colors))

    # Known symmetry reduction
    prefix = [(0, 0)]
    for_all_deals(args.depth - 1, args.num_colors, callback, prefix)
    prefix = [(0, 1)]
    for_all_deals(args.depth - 1, args.num_colors, callback, prefix)

    print("Found", len(canonized), "unique sequences.")
    if args.outfile:
        with open(args.outfile, 'w') as f:
            json.dump(sorted(canonized), f)
        print("Saved result to", args.outfile)
