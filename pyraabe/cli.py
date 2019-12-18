import argparse
import pyraabe
import os


def main():
    """
    Command line interface for PyRaabe functionality.

    """

    # init
    parser = argparse.ArgumentParser(description='PyRaabe: automated Raabe table generation')

    # args
    parser.add_argument('-v', '--version', action='version', version=pyraabe.__version__, help='print version and exit')
    parser.add_argument('infile', type=str, help='path to input .stl file with open inlet/outlets (str)')
    parser.add_argument('outdir', type=str, help='path to output folder (str)')
    parser.add_argument('-g', '--gravity', nargs='+', type=int, default=[0, -1, 0], help='gravity direction vector (int, default=0 -1 0)')

    # parse
    args = parser.parse_args()

    # check gravity vector
    if len(args.gravity) != 3:
        raise ValueError('gravity vector must be length 3')

    # output directory
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    # outputs
    basename = os.path.splitext(os.path.basename(args.infile))[0]
    centerline = basename + '_centerline.vtp'
    raabe = basename + '_raabe.tsv'

    # centerline extraction
    pyraabe.centerline.compute(args.infile, centerline)

    # raabe generation
    pyraabe.table.generate(centerline, gravity_vector=args.gravity).to_csv(raabe, sep='\t', index=False)
