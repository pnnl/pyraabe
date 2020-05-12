import subprocess
import pandas as pd
from vmtk import vmtkscripts


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

    # read surface
    centerlineReader = vmtkscripts.vmtkSurfaceReader()
    centerlineReader.InputFileName = infile
    centerlineReader.Execute()

    # centerline
    centerline = vmtkscripts.vmtkCenterlines()
    centerline.Surface = centerlineReader.Surface
    centerline.SeedSelectorName = 'openprofiles'
    centerline.AppendEndPoints = 1
    centerline.Execute()

    # extract branches
    branchExtractor = vmtkscripts.vmtkBranchExtractor()
    branchExtractor.Centerlines = centerline.Centerlines
    branchExtractor.Execute()

    # merge centerlines
    centerlineMerge = vmtkscripts.vmtkCenterlineMerge()
    centerlineMerge.Centerlines = branchExtractor.Centerlines
    centerlineMerge.Execute()

    # write surface
    centerlineWriter = vmtkscripts.vmtkSurfaceWriter()
    centerlineWriter.OutputFileName = outfile
    centerlineWriter.Surface = centerlineMerge.Centerlines
    centerlineWriter.Execute()


def read(infile):
    """
    Reads VMTK centerline file.

    Parameters
    ----------
    ifile : str
        Path to input VMTK centerline file (.vtp format).

    Returns
    -------
    centerline : dict
        Dictionary of arrays defining the centerline.

    """

    # read surface
    centerlineReader = vmtkscripts.vmtkSurfaceReader()
    centerlineReader.InputFileName = infile
    centerlineReader.Execute()

    # numpy adaptor
    clNumpyAdaptor = vmtkscripts.vmtkCenterlinesToNumpy()
    clNumpyAdaptor.Centerlines = centerlineReader.Surface
    clNumpyAdaptor.ConvertCellToPoint = 1
    clNumpyAdaptor.Execute()

    return clNumpyAdaptor.ArrayDict


def to_dataframe(centerline):
    """
    Converts VMTK centerline to Pandas DataFrame.

    Parameters
    ----------
    centerline : dict
        Dictionary of arrays defining the centerline.

    Returns
    -------
    centerline : DataFrame
        Data frame containing centerline information.

    """

    df = pd.DataFrame({k: v for k, v in centerline['PointData'].items() if len(v.shape) < 2})
    df2 = pd.DataFrame(data=centerline['Points'], columns=['x', 'y', 'z'])
    return pd.concat((df2, df), axis=1)
