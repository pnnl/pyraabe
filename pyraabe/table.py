import numpy as np
import pandas as pd
import pyraabe
import math


def angle(v1, v2):
    """
    Computes angle between two vectors.

    Parameters
    ----------
    v1, v2 : ndarray
        Vectors that form the angle.

    Returns
    -------
    angle : float
        Angle in degrees.

    """

    return np.degrees(np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))))


def arclength(points):
    """
    Computes arc length between a sequence of points. Assumes
    points are ordered.

    Parameters
    ----------
    points : ndarray
        An mxn array of m points over which the arc length is calculated.

    Returns
    -------
    length : float
        Arc length.

    """

    return np.sum([np.sum(np.sqrt(np.square(points[i] - points[i + 1]))) for i in range(len(points) - 1)])


def generate(infile, gravity_vector=[0, 0, 0]):
    """
    Generates Raabe table from extracted VMTK centerline data.

    Parameters
    ----------
    infile : str
        Path to input VMTK centerline file (.vtp format).
    gravity_vector : list
        Vector definining gravity direction.

    Returns
    -------
    raabe_table : DataFrame
        Data frame containing Raabe table information.

    """

    # iterator to count raabe indices
    class Iterator:
        def __init__(self):
            self.i = 1

        def get(self):
            j = str(self.i)
            self.i -= 1

            return j

    # check gravity vector
    if len(gravity_vector) != 3:
        raise ValueError('gravity vector must be length 3')

    # load centerline
    centerline = pyraabe.centerline.read(infile)

    # parse centerline
    df = pyraabe.centerline.to_dataframe(centerline)
    connectivity = centerline['CellData']['CellPointIds']

    # initialize containers
    queue = [0]

    result = {'raabe': [None for x in range(len(connectivity))],
              'bifurcation_angle': [0 for x in range(len(connectivity))],
              'gravity_angle': [None for x in range(len(connectivity))],
              'length': [None for x in range(len(connectivity))],
              'diameter': [None for x in range(len(connectivity))],
              'daughter_branches': [[] for x in range(len(connectivity))]}

    result['raabe'][0] = "1"

    # diameter
    result['diameter'] = [2 * df.loc[idx, 'MaximumInscribedSphereRadius'].mean() for idx in connectivity]

    # length
    for i, idx in enumerate(connectivity):
        points = df.loc[idx, ['x', 'y', 'z']].values
        result['length'][i] = arclength(points)

    # gravity angle
    for i, idx in enumerate(connectivity):
        result['gravity_angle'][i] = angle(df.loc[idx[-1], ['x', 'y', 'z']] - df.loc[idx[0], ['x', 'y', 'z']],
                                           np.array(gravity_vector))

    while len(queue) > 0:
        # first item in queue
        i = queue.pop(0)

        # extract segment
        x = connectivity[i]

        # initial connectivity pass
        tmp = []
        for j, y in enumerate(connectivity):
            if x[-1] == y[0]:
                tmp.append([result['diameter'][j], j])

        # sort by radius (largest first)
        tmp.sort(reverse=True)

        # second pass
        lr = Iterator()
        for d, j in tmp:
            # add to tree queue
            queue.append(j)

            # append daughter connectivity
            result['daughter_branches'][i].append(j)

            # update raabe table
            result['raabe'][j] = result['raabe'][i] + lr.get()

            # calculate bifurcation angle
            result['bifurcation_angle'][j] = angle(df.loc[connectivity[j][-1], ['x', 'y', 'z']] - df.loc[connectivity[j][0], ['x', 'y', 'z']],
                                                   df.loc[connectivity[i][-1], ['x', 'y', 'z']] - df.loc[connectivity[i][0], ['x', 'y', 'z']])

    # cast as dataframe
    result = pd.DataFrame(result)
    result['approx_volume'] = result['length'] * np.square(result['diameter'] / 2) * np.pi
    return result[['raabe', 'diameter', 'length', 'bifurcation_angle', 'gravity_angle', 'approx_volume', 'daughter_branches']]
