import subprocess
from pkg_resources import resource_filename
import os


def extract(infile, outfile):
    """
    Calls VMTK routine for centerline extraction.

    Parameters
    ----------
    infile : string
        Path to input mesh with open inlet/outlets (.stl format).
    outfile : string
        Path to output centerline (.vtp format).

    Returns
    -------
    None

    """

    subprocess.call([resource_filename('pyraabe', 'shell/centerline.sh'), infile, outfile])


def nodes(infile, outfile):
    """
    Calls VMTK routine for centerline extraction.

    Parameters
    ----------
    infile : string
        Path to input centerline (.vtp format).
    outfile : string
        Path to output node locations (.vtp format).

    Returns
    -------
    None

    """

    subprocess.call([resource_filename('pyraabe', 'shell/nodes.sh'), infile, outfile])


def merge(infile, outfile):
    """
    Calls VMTK routine to merge centerline paths.

    Parameters
    ----------
    infile : string
        Path to unmerged input centerline (.vtp format).
    outfile : string
        Path to output merged centerline (.vtp format).

    Returns
    -------
    None

    """

    subprocess.call([resource_filename('pyraabe', 'shell/merge.sh'), infile, outfile])


def compute(infile, outdir):
    """
    Convenience function to perform all VMTK routines
    for centerline extraction and processing. Filenames
    and formats are handled automatically.

    Parameters
    ----------
    infile : string
        Path to input mesh with open inlet/outlets (.stl format).
    outfile : string
        Path to output directory.

    Returns
    -------
    None

    """

    # paths
    basename = os.path.splitext(os.path.basename(infile))[0]
    path = {'tmp': os.path.join(outdir, basename + '_centerline.tmp.vtp'),
            'centerline': os.path.join(outdir, basename + '_centerline.vtp'),
            'nodes': os.path.join(outdir, basename + '_nodes.vtp'),
            'merged': os.path.join(outdir, basename + '_centerline.vtp')}

    # compute centerline
    extract(infile, path['tmp'])

    # extract nodes
    nodes(path['tmp'], path['nodes'])

    # merge centerline
    merge(path['tmp'], path['centerline'])
