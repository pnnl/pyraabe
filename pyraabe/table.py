import numpy as np
import pandas as pd
import pyraabe


def angle(a, b, c):
    """
    Computes angle between three points.

    Parameters
    ----------
    a, b, c : ndarray
        Coordinate of each point to form the angle.

    Returns
    -------
    angle : float
        Angle in degrees.

    """

    ba = a - b
    bc = c - b

    return np.degrees(np.arccos(np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))))


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


def generate(infile, gravity_vector=[0, -1, 0]):
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
            self.i = 0

        def get(self):
            j = str(self.i)
            self.i += 1

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
    raabe = [None for x in range(len(connectivity))]
    angles = [None for x in range(len(connectivity))]
    gravang = [None for x in range(len(connectivity))]
    lengths = [None for x in range(len(connectivity))]
    raabe[0] = "0"

    # diameter
    diam = [2 * df.loc[idx, 'MaximumInscribedSphereRadius'].mean() for idx in connectivity]

    # length
    for i, idx in enumerate(connectivity):
        points = df.loc[idx, ['x', 'y', 'z']].values
        lengths[i] = arclength(points)

    # gravity angle
    for i, idx in enumerate(connectivity):
        gravang[i] = angle(df.loc[idx[0], ['x', 'y', 'z']] + np.array(gravity_vector),
                           df.loc[idx[0], ['x', 'y', 'z']],
                           df.loc[idx[-1], ['x', 'y', 'z']])

    while len(queue) > 0:
        # first item in queue
        i = queue.pop(0)

        # extract segment
        x = connectivity[i]

        # initial connectivity pass
        tmp = []
        for j, y in enumerate(connectivity):
            if x[-1] == y[0]:
                tmp.append([diam[j], j])

        # sort by radius (largest first)
        tmp.sort(reverse=True)

        # second pass
        connected = []
        lr = Iterator()
        for d, j in tmp:
            queue.append(j)
            connected.append(j)
            raabe[j] = raabe[i] + lr.get()

        # calculate bifurcation angle
        if len(connected) > 1:
            angles[i] = angle(df.loc[connectivity[connected[0]], ['x', 'y', 'z']].values.mean(axis=0),
                              df.loc[x[-1], ['x', 'y', 'z']].values,
                              df.loc[connectivity[connected[1]], ['x', 'y', 'z']].values.mean(axis=0))
        else:
            angles[i] = np.nan

    return pd.DataFrame({'raabe': raabe, 'bifurcation_angle': angles, 'gravity_angle': gravang, 'diameter': diam, 'length': lengths})
