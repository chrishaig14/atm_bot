import numpy as np
import pandas as pd
from kdtree import *

r = 6371000
pi = 3.14159265


def dist_euclidean(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def dist_haversine(a, b):
    long1, lat1 = a
    long2, lat2 = b
    return 2 * r * np.arcsin(
        np.sqrt(np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((long2 - long1) / 2) ** 2))


data = pd.read_csv("cajeros-automaticos.csv")

points_long_lat = data[['long', 'lat']].to_numpy() * pi / 180  # in radians

# print(dist_euclidean(a, b))
# print(dist_haversine(a, b))
#
# exit(0)

points_x_y = np.array(points_long_lat)  # convert to cartesian x y coordinates
l0 = np.median(points_long_lat[:, 1])
print(np.cos(l0))
points_x_y[:, 0] = r * points_x_y[:, 0] * np.cos(l0)
points_x_y[:, 1] = r * points_x_y[:, 1]

n = 100
d_e = np.zeros((n, n))
d_h = np.zeros((n, n))

t_e = np.zeros((n, n))
t_h = np.zeros((n, n))

for i in range(n):
    for j in range(n):
        s = time.time()
        d_e[i][j] = dist_euclidean(points_x_y[i], points_x_y[j])
        e = time.time()
        t_e[i][j] = e - s
        s = time.time()
        d_h[i][j] = dist_haversine(points_long_lat[i], points_long_lat[j])
        e = time.time()
        t_h[i][j] = e - s
        print(d_h[i][j], d_e[i][j])

diff = np.abs(d_e - d_h)

min = np.min(diff)
max = np.max(diff)
avg = np.average(diff)
std = np.std(diff)
print(min, max, avg, std)

print("t_e: ", np.average(t_e))
print("t_h: ", np.average(t_h))

# a = np.array([-58.7407808, -34.5412715])*pi/180
# b = np.array([-58.6636343, -34.5649629])*pi/180
#
# ea = np.array(a)
# ea[0] = r * ea[0] * np.cos(l0)
# ea[1] = r * ea[1]
# eb = np.array(b)
# eb[0] = r * eb[0] * np.cos(l0)
# eb[1] = r * eb[1]
#
# print(dist_euclidean(ea, eb))
#
# ha = a
# hb = b
#
# print(dist_haversine(ha, hb))
