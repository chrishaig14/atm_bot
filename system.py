import pandas as pd
from kdtree import *

PI = 3.14159265
R = 6371000  # Earth radius in meters


class System:
    def __init__(self):
        self.points_long_lat = pd.read_csv("cajeros-automaticos.csv")
        self.points_long_lat_rad = (self.points_long_lat[['long', 'lat']] * PI / 180).to_numpy()

        self.l0 = np.median(self.points_long_lat_rad[:, 1])  # median latitude
        self.points_x_y = np.array(self.points_long_lat_rad)
        self.points_x_y[:, 0] = R * self.points_x_y[:, 0] * np.cos(self.l0)
        self.points_x_y[:, 1] = R * self.points_x_y[:, 1]

        self.points = [Point(i, [p[0],p[1]]) for i, p in enumerate(self.points_x_y)]


        self.kd_link = make_kdtree(self.points, axis=0)
        self.kd_banelco = make_kdtree(self.points, axis=0)

    def search_nearest(self, lat, long, net):
        kd_search = None
        if net == "LINK":
            kd_search = self.kd_link
        elif net == "BANELCO":
            kd_search = self.kd_banelco
        q = [long * PI / 180, lat * PI / 180]
        q[0] = R * q[0] * np.cos(self.l0)
        q[1] = R * q[1]
        results = search_closest_kdtree(kd_search, q, 3)
        print("RESULTSIII: ", results)
        r = self.points_long_lat.iloc[results]
        plt.scatter([p.xy[0] for p in self.points],[p.xy[1] for p in self.points], color="b")
        plt.scatter(q[0],q[1],color="g")
        plt.show()
        return r

if __name__=='__main__':


    s = System()
    result = s.search_nearest(-34, -58, 'LINK')
    print(result)
    l = ["{}".format(r['ubicacion']) for i, r in result.iterrows()]
    print(l)
    for i, r in result.iterrows():
        plt.scatter(r['long'], r['lat'],color="r")
    plt.scatter(-58,-34,color="g")
    plt.show()
