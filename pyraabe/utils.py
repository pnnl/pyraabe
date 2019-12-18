from vmtk import vmtkscripts
import pandas as pd


def read_centerline(infile):
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

    centerlineReader = vmtkscripts.vmtkSurfaceReader()
    centerlineReader.InputFileName = infile
    centerlineReader.Execute()
    clNumpyAdaptor = vmtkscripts.vmtkCenterlinesToNumpy()
    clNumpyAdaptor.Centerlines = centerlineReader.Surface
    clNumpyAdaptor.ConvertCellToPoint = 1
    clNumpyAdaptor.Execute()
    return clNumpyAdaptor.ArrayDict


def centerline2dataframe(centerline):
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
