import numpy as np
import pandas as pd
import pyraabe
import os


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


def generate(centerline, gravity_vector=[0, 0, 0], extruded=False):
    """
    Generates Raabe table from extracted VMTK centerline data.

    Parameters
    ----------
    centerline : dict
        Centerline loaded from VTP file.
    gravity_vector : list
        Vector definining gravity direction.
    extruded : bool
        Signals whether the inlet was artificially extruded.

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
              'daughter_branches': [[] for x in range(len(connectivity))],
              'endpoint_idx': [None for x in range(len(connectivity))]}

    result['raabe'][0] = "1"

    # diameter
    result['diameter'] = [2 * df.loc[idx[2:], 'MaximumInscribedSphereRadius'].median() for idx in connectivity]

    # length
    for i, idx in enumerate(connectivity):
        points = df.loc[idx, ['x', 'y', 'z']].values
        result['length'][i] = arclength(points)
        if i > 0:
            result['length'][i] = result['length'][i] - df.loc[idx[0], 'MaximumInscribedSphereRadius']

        # endpoint index
        result['endpoint_idx'][i] = connectivity[i][-1]

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

        # sort daughter indices
        result['daughter_branches'][i].sort()

    # terminal branches
    result['daughter_branches'] = [x if x != [] else np.nan for x in result['daughter_branches']]

    # cast as dataframe
    result = pd.DataFrame(result)
    result['approx_volume'] = result['length'] * np.square(result['diameter'] / 2) * np.pi

    # nullify extruded section
    if extruded:
        result.loc[0, ['diameter', 'length', 'bifurcation_angle', 'gravity_angle', 'approx_volume']] = np.nan

    return result[['raabe', 'diameter', 'length', 'bifurcation_angle', 'gravity_angle', 'approx_volume', 'daughter_branches', 'endpoint_idx']]


def merge(parent, children, gravity_vector=[0, 1, 0], extruded=False):
    """
    Generates merged Raabe table from multiple extracted VMTK centerline data.

    Parameters
    ----------
    parent : dict
        Parent centerline loaded from VTP file.
    children : list of dicts
        Child centerlines loaded from VTP file.
    gravity_vector : list
        Vector definining gravity direction.
    extruded : bool
        Signals whether the inlet was artificially extruded.

    Returns
    -------
    raabe_table : DataFrame
        Data frame containing merged Raabe table information.
    all_tables : list of DataFrames
        Individual Raabe tables.

    """

    all_tables = []

    parent_ctrline = pyraabe.centerline.read(parent)
    parent_raabe = generate(parent_ctrline, gravity_vector=gravity_vector, extruded=extruded)

    all_tables.append(parent_raabe.copy())

    parent_raabe['source'] = os.path.basename(parent).split('_', 1)[0]

    for child in children:
        child_ctrline = pyraabe.centerline.read(child)
        child_raabe = generate(child_ctrline, gravity_vector=gravity_vector, extruded=extruded)

        all_tables.append(child_raabe.copy())

        child_raabe['endpoint_idx'] = np.nan
        child_raabe['source'] = os.path.basename(child).split('_', 1)[0]

        idx, coord = pyraabe.centerline.match(parent_ctrline, child_ctrline)
        prefix = parent_raabe.loc[parent_raabe['endpoint_idx'] == idx, 'raabe'].values[0]
        a = parent_raabe.loc[parent_raabe['endpoint_idx'] == idx, 'bifurcation_angle'].values[0]
        n = len(parent_raabe.index)

        child_raabe.loc[0, 'bifurcation_angle'] = a
        child_raabe['raabe'] = child_raabe['raabe'].str[1:]
        child_raabe['raabe'] = prefix + child_raabe['raabe']
        child_raabe.index += n
        child_raabe['daughter_branches'] = [(np.array(x) + n).tolist() for x in child_raabe['daughter_branches']]

        parent_raabe = pd.concat((parent_raabe, child_raabe), axis=0)

    return parent_raabe, all_tables
