import argparse
import pyraabe


def main():
    """
    Command line interface for PyRaabe functionality.

    """

    # init
    parser = argparse.ArgumentParser(description='PyRaabe: automated Raabe table generation')

    # args
    parser.add_argument('-v', '--version', action='version', version=pyraabe.__version__, help='print version and exit')
    parser.add_argument('infile', type=str, help='path to input .stl file with open inlet/outlets')
    parser.add_argument('outdir', type=str, help='path to output folder')

    # parse
    args = parser.parse_args()

    # run
    pyraabe.centerline.compute(args.infile, args.outdir)
