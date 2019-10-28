import time

import numpy as np
import matplotlib.pyplot as plt





class Point:
    def __init__(self, ID, xy):
        self.ID = ID
        self.xy = xy

    def __repr__(self):
        return "Point(" + str(self.ID) + "," + str(self.xy) + "]"


def generate_random_points(n, xmin, ymin, xmax, ymax):
    points = np.random.rand(n, 2)
    points[:, 0] = points[:, 0] * (xmax - xmin) + xmin
    points[:, 1] = points[:, 1] * (ymax - ymin) + ymin
    return points


def plot_points(points):
    plt.scatter([p.xy[0] for p in points], [p.xy[1] for p in points], color="k", zorder=1)


class Node:
    def __init__(self, axis):
        self.axis = axis
        self.point = None
        self.left = None
        self.right = None

def make_kdtree(points: [Point], axis):
    # axis 0 => x, split horizontally
    # axis 1 => y, split vertically
    if len(points) == 0:
        return None
    tree = Node(axis)
    tree.point = points[0]
    left = list(filter(lambda p: p.xy[axis] < tree.point.xy[axis], points))
    right = list(filter(lambda p: p.xy[axis] > tree.point.xy[axis], points))
    tree.left = make_kdtree(left, (axis + 1) % 2)
    tree.right = make_kdtree(right, (axis + 1) % 2)
    return tree


def plot_kdtree(tree, xmin, xmax, ymin, ymax):
    if tree is None:
        return
    if tree.axis == 0:
        # split vertically
        plt.plot([tree.point.xy[0], tree.point.xy[0]], [ymin, ymax], color="r", zorder=0)
        plot_kdtree(tree.left, xmin, tree.point.xy[0], ymin, ymax)
        plot_kdtree(tree.right, tree.point.xy[0], xmax, ymin, ymax)
    if tree.axis == 1:
        # split horizontally
        plt.plot([xmin, xmax], [tree.point.xy[1], tree.point.xy[1]], color="b", zorder=0)
        plot_kdtree(tree.right, xmin, xmax, tree.point.xy[1], ymax)
        plot_kdtree(tree.left, xmin, xmax, ymin, tree.point.xy[1])


def distance(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def search_closest_kdtree_rec(tree, q, best):
    if tree is None:
        return
    d = distance(tree.point.xy, q)
    if d < best[-1]['distance']:
        best.append({"point": tree.point, "distance": d})
        best.sort(key=lambda x: x["distance"])
        best[:] = best[:-1]

    if q[tree.axis] > tree.point.xy[tree.axis]:
        # search right
        search_closest_kdtree_rec(tree.right, q, best)
        # there might be a best solution on the left side anyway
        if q[tree.axis] - best[-1]["distance"] < tree.point.xy[tree.axis]:
            search_closest_kdtree_rec(tree.left, q, best)
    else:
        # search left
        search_closest_kdtree_rec(tree.left, q, best)
        # there might be a best solution on the right side anyway
        if q[tree.axis] + best[-1]["distance"] > tree.point.xy[tree.axis]:
            search_closest_kdtree_rec(tree.right, q, best)


def search_closest_kdtree(tree, q, num):
    best = [{'point': [], 'distance': float('inf')}] * num
    search_closest_kdtree_rec(tree, q, best)
    return [x["point"].ID for x in best]


def search_closest(points, q, n):
    distances = [{'point': p, 'distance': distance(p.xy, q)} for p in points]
    distances.sort(key=lambda p: p['distance'])
    return [p["point"] for p in distances[:n]]


def main():
    n = 500
    xmin = 0
    xmax = 100
    ymin = 0
    ymax = 100
    points = generate_random_points(n, xmin, ymin, xmax, ymax)

    points = [Point(i,[p[0],p[1]]) for i,p in enumerate(points)]
    p_dict = {p.ID:[p.xy[0],p.xy[1]] for p in points}
    tree = make_kdtree(points,axis=0)

    
    q = [54,70]
    results = search_closest_kdtree(tree,q,23)

    # plot original points

    plt.scatter([p[0] for p in p_dict.values()], [p[1] for p in p_dict.values()], color="b")

    # plot query point

    plt.scatter(q[0],q[1],color="g")

    # plot results

    plt.scatter([p_dict[id][0] for id in results], [p_dict[id][1] for id in results], color="r")



    plt.show()




if __name__ == '__main__':
    main()
