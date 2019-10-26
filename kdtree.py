import time

import numpy as np
import matplotlib.pyplot as plt


def generate_random_points(n, xmin, ymin, xmax, ymax):
    points = np.random.rand(n, 2)
    points[:, 0] = points[:, 0] * (xmax - xmin) + xmin
    points[:, 1] = points[:, 1] * (ymax - ymin) + ymin
    return points


def plot_points(points):
    plt.scatter(points[:, 0], points[:, 1], color="k", zorder=1)


class Node:
    def __init__(self, axis):
        self.axis = axis
        self.point = []
        self.left = None
        self.right = None


def make_kdtree(points, axis):
    # axis 0 => x, split horizontally
    # axis 1 => y, split vertically
    if len(points) == 0:
        return None
    tree = Node(axis)
    tree.point = points[0]
    tree.left = make_kdtree(points[points[:, axis] < tree.point[axis]], (axis + 1) % 2)
    tree.right = make_kdtree(points[points[:, axis] > tree.point[axis]], (axis + 1) % 2)
    return tree


def plot_kdtree(tree, xmin, xmax, ymin, ymax):
    if tree is None:
        return
    if tree.axis == 0:
        # split vertically
        plt.plot([tree.point[0], tree.point[0]], [ymin, ymax], color="r", zorder=0)
        plot_kdtree(tree.left, xmin, tree.point[0], ymin, ymax)
        plot_kdtree(tree.right, tree.point[0], xmax, ymin, ymax)
    if tree.axis == 1:
        # split horizontally
        plt.plot([xmin, xmax], [tree.point[1], tree.point[1]], color="b", zorder=0)
        plot_kdtree(tree.right, xmin, xmax, tree.point[1], ymax)
        plot_kdtree(tree.left, xmin, xmax, ymin, tree.point[1])


def distance(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def search_closest_kdtree_rec(tree, q, best):
    if tree is None:
        return
    d = distance(tree.point, q)
    if d < best[-1]['distance']:
        best.append({"point": tree.point, "distance": d})
        best.sort(key=lambda x: x["distance"])
        best[:] = best[:-1]

    if q[tree.axis] > tree.point[tree.axis]:
        # search right
        search_closest_kdtree_rec(tree.right, q, best)
        # there might be a best solution on the left side anyway
        if q[tree.axis] - best[-1]["distance"] < tree.point[tree.axis]:
            search_closest_kdtree_rec(tree.left, q, best)
    else:
        # search left
        search_closest_kdtree_rec(tree.left, q, best)
        # there might be a best solution on the right side anyway
        if q[tree.axis] + best[-1]["distance"] > tree.point[tree.axis]:
            search_closest_kdtree_rec(tree.right, q, best)


def search_closest_kdtree(tree, q, num):
    best = [{'point': [], 'distance': float('inf')}] * num
    search_closest_kdtree_rec(tree, q, best)
    return [x["point"] for x in best]


def search_closest(points, q, n):
    distances = [{'point': p, 'distance': distance(p, q)} for p in points]
    distances.sort(key=lambda p: p['distance'])
    return [p["point"] for p in distances[:n]]


def main():
    n = 500
    xmin = 0
    xmax = 100
    ymin = 0
    ymax = 100
    points = generate_random_points(n, xmin, ymin, xmax, ymax)
    print("Building kd-tree...")
    tree = make_kdtree(points, axis=0)
    print("Done")
    plot_kdtree(tree, xmin, xmax, ymin, ymax)
    plot_points(points)

    q = [23, 17]
    num = 10
    s = time.time()
    result = search_closest_kdtree(tree, q, num)
    e = time.time()
    t_kd = e - s
    s = time.time()
    brute_result = search_closest(points, q, num)
    e = time.time()
    t_brute = e - s
    print("time kd: ", t_kd)
    print("time brute: ", t_brute)

    print(brute_result)
    print(result)

    assert (np.array(brute_result) == np.array(result)).all()

    plt.scatter([r[0] for r in result], [r[1] for r in result], color="r")
    plt.scatter(q[0], q[1], color="g")
    plt.show()


if __name__ == '__main__':
    main()
