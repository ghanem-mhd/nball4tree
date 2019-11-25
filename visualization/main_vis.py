import os
import argparse
from visualization.generate_tree import generate_files
from visualization.transformation_2d import do_all


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-g', '--gen',  action='store_true')
    parser.add_argument('--w2v')
    parser.add_argument('--sample')
    parser.add_argument('--input')
    parser.add_argument('--output')
    parser.add_argument('-v', '--vis',  action='store_true')
    parser.add_argument('--balls')
    parser.add_argument('--children')

    args = parser.parse_args()
    if args.gen:
        if args.w2v and (args.input or args.sample) and args.output:
            print("Start generating files...")
            generate_files(args.w2v, args.input, args.sample, args.output)
            print("Finish generating files...")

    if args.vis:
        if args.balls and args.children:
            do_all(args.balls, args.children)


if __name__ == "__main__":
    main()
