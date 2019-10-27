import numpy as np
import matplotlib.pyplot as plt

import pandas as pd

from kdtree import *

data = pd.read_csv("cajeros-automaticos.csv")

xmin = data['long'].min()
xmax = data['long'].max()
ymin = data['lat'].min()
ymax = data['lat'].max()

print(xmin)

banelco = data[data['red'] == 'BANELCO']
link = data[data['red'] == 'LINK']

p_link = link[['long', 'lat']].to_numpy()

plt.scatter(p_link[:, 0], p_link[:, 1])
plt.show()

kd_link = make_kdtree(p_link, axis=0)
plot_points(p_link)
num = 3
q = [(xmax + xmin) / 2, (ymax + ymin) / 2]
b = search_closest_kdtree(kd_link, q, num)
b = np.array(b)
plt.scatter(b[:, 0], b[:, 1], color='b')
plt.scatter(q[0], q[1], color='g')
plt.show()
