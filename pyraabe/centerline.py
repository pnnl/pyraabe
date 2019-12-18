import subprocess
from pkg_resources import resource_filename


def compute(infile, outfile):
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

    # compute centerline
    subprocess.call([resource_filename('pyraabe', 'shell/centerline.sh'), infile, outfile])
