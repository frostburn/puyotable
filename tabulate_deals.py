import argparse
import json
from multiprocessing import Pool

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


def unique_deals(num_deals, num_colors, prefix_=[]):
    canonized = set()

    def callback(deals):
        canonized.add(canonize_deals(deals, num_colors))

    # Known symmetry reduction
    prefix = [(0, 0)] + prefix_
    for_all_deals(num_deals - 1, num_colors, callback, prefix)
    prefix = [(0, 1)] + prefix_
    for_all_deals(num_deals - 1, num_colors, callback, prefix)

    return canonized


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

    if args.depth > 1:
        prefixes = [[(c0, c1)] for c0 in range(args.num_colors) for c1 in range(args.num_colors)]  # noqa

        process_args = [
            (args.depth - 1, args.num_colors, prefix) for prefix in prefixes
        ]
        pool = Pool()
        subsets = pool.starmap(unique_deals, process_args)
        for subset in subsets:
            canonized.update(subset)
    else:
        canonized = unique_deals(args.depth, args.num_colors)

    print("Found", len(canonized), "unique sequences.")
    if args.outfile:
        with open(args.outfile, 'w') as f:
            json.dump(sorted(canonized), f)
        print("Saved result to", args.outfile)
