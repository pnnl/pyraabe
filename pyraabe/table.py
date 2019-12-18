import numpy as np
import pandas as pd
import pyraabe


def angle(a, b, c):
    ba = a - b
    bc = c - b

    return np.degrees(np.arccos(np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))))


def arclength(points):
    return np.sum([np.sum(np.sqrt(np.square(points[i] - points[i + 1]))) for i in range(len(points) - 1)])


def generate(infile):

    # iterator to count raabe indices
    class Iterator:
        def __init__(self):
            self.i = 0

        def get(self):
            j = str(self.i)
            self.i += 1

            return j

    # load centerline
    centerline = pyraabe.utils.read_centerline(infile)

    # parse centerline
    df = pyraabe.utils.centerline2dataframe(centerline)
    connectivity = centerline['CellData']['CellPointIds']

    # diameter
    diam = [2 * df.loc[idx, 'MaximumInscribedSphereRadius'].mean() for idx in connectivity]

    # length
    lengths = []
    for idx in connectivity:
        points = df.loc[idx, ['x', 'y', 'z']].values
        lengths.append(arclength(points))

    # initialize containers
    queue = [0]
    raabe = [None for x in range(len(connectivity))]
    angles = [None for x in range(len(connectivity))]
    raabe[0] = "0"

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

    return pd.DataFrame({'raabe': raabe, 'bifurcation_angle': angles, 'diameter': diam, 'length': lengths})
