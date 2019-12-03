import argparse
from generate_tree import generate_files
from transformation_2d import reduce_and_fix, visualize

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
    parser.add_argument('-rf', '--reduceAndFix', action='store_true')
    parser.add_argument('--circles')
    parser.add_argument('--showenWords')

    args = parser.parse_args()
    if args.gen:
        if args.w2v and (args.input or args.sample) and args.output:
            print("Start generating files...")
            generate_files(args.w2v, args.input, args.sample, args.output)
            print("Finish generating files...")

    if args.reduceAndFix:
        if args.balls and args.children and args.output:
            reduce_and_fix(args.balls, args.children, args.output)

    if args.vis and args.circles and args.showenWords:
        visualize(args.circles, args.showenWords)


if __name__ == "__main__":
    main()
