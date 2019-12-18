from vmtk import vmtkscripts
import pandas as pd


def read_centerline(infile):
    centerlineReader = vmtkscripts.vmtkSurfaceReader()
    centerlineReader.InputFileName = infile
    centerlineReader.Execute()
    clNumpyAdaptor = vmtkscripts.vmtkCenterlinesToNumpy()
    clNumpyAdaptor.Centerlines = centerlineReader.Surface
    clNumpyAdaptor.ConvertCellToPoint = 1
    clNumpyAdaptor.Execute()
    return clNumpyAdaptor.ArrayDict


def centerline2dataframe(arr):
    df = pd.DataFrame({k: v for k, v in arr['PointData'].items() if len(v.shape) < 2})
    df2 = pd.DataFrame(data=arr['Points'], columns=['x', 'y', 'z'])
    return pd.concat((df2, df), axis=1)
