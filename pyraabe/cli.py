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
    parser.add_argument('infile', type=str, help='path to input .stl file with open inlet/outlets.')
    parser.add_argument('outdir', type=str, help='path to output folder')
    parser.add_argument('-a', '--append', type=str, nargs='+', metavar='PATHS', help='additional subtrees to append')
    parser.add_argument('-g', '--gravity', nargs=3, type=int, default=[0, 0, 0], required=True, metavar=('x', 'y', 'z'),
                        help='gravity direction vector, e.g.: 0 1 0 for +Y direction')
    parser.add_argument('-e', '--extruded', action='store_true',
                        help='signal whether the inlet has been artificially extruded')

    # parse
    args = parser.parse_args()

    # output directory
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    infiles = [args.infile]

    if args.append is not None:
        infiles += args.append

    # iterate inputs
    centerline_paths = []
    raabe_paths = []
    for infile in infiles:
        # outputs
        basename = os.path.splitext(os.path.basename(infile))[0]
        centerline_path = os.path.join(args.outdir, basename + '_centerline.vtp')
        centerline_paths.append(centerline_path)
        raabe_path = os.path.join(args.outdir, basename + '_raabe.tsv')
        raabe_paths.append(raabe_path)

        # centerline extraction
        if not os.path.exists(centerline_path):
            pyraabe.centerline.compute(infile, centerline_path)
        else:
            print('{} already exists. Skipping centerline calculation.'.format(centerline_path))

    # merge
    if len(centerline_paths) > 1:
        raabe, raabe_all = pyraabe.table.merge(centerline_paths[0],
                                               centerline_paths[1:],
                                               gravity_vector=args.gravity,
                                               extruded=args.extruded)

        # save individual raabes
        for i in range(len(raabe_paths)):
            raabe_all[i].drop(columns='endpoint_idx').to_csv(raabe_paths[i], sep='\t')

        # save merged raabe
        raabe.drop(columns='endpoint_idx').to_csv(os.path.join(args.outdir, 'merged_raabe.tsv'), sep='\t')

    # single
    else:
        # read in centerline
        centerline = pyraabe.centerline.read(centerline_path)

        # raabe generation
        raabe = pyraabe.table.generate(centerline, gravity_vector=args.gravity, extruded=args.extruded)

        # drop column and save
        raabe.drop(columns='endpoint_idx').to_csv(raabe_path, sep='\t')
