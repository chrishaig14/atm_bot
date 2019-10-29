import numpy as np


# KD TREE TO SEARCH N NEAREST NEIGHBOURS

# points is a list of Point(id,xy)
# id is int
# xy is list of 2d coords
# tree = make_kdtree(points,axis=0)
# search_closest_kdtree(tree,q,n) returns list of {'point':id, 'distance':xx}
# where q = list of 2d coords (x,y)
# and n = number of nearest neighbours we want


class Point:
    def __init__(self, ID, xy, active):
        self.ID = ID
        self.xy = xy
        self.active = active

    def __repr__(self):
        return "Point(" + str(self.ID) + "," + str(self.xy) + "]"


class Node:
    def __init__(self, axis):
        self.axis = axis
        self.point = None
        self.left = None
        self.right = None


def make_kdtree(points, axis):
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


def distance(a, b):
    # euclidean distance
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def search_closest_kdtree_rec(tree, q, best):
    if tree is None:
        return
    if tree.point.active:
        # only consider this point as a potential result if it is active
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
    return best
