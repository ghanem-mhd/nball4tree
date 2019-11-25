import os
import argparse


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-g', '--gen',  action='store_true')
    parser.add_argument('--words')
    parser.add_argument('--w2v')
    parser.add_argument('-v', '--vis',  action='store_true')

    args = parser.parse_args()
    if args.gen:
        print("Generate tree files")

    if args.vis:
        print("Vis")


if __name__ == "__main__":
    main()
