import pandas as pd
from kdtree import *

PI = 3.14159265
R = 6371000  # Earth radius in meters


class System:
    def __init__(self):
        self.points_long_lat = pd.read_csv("cajeros-automaticos.csv")
        self.points_long_lat_rad = self.points_long_lat.copy() # deep copy to keep original intact
        self.points_long_lat_rad[['long','lat']]=self.points_long_lat_rad[['long','lat']]*PI/180
        # self.points_long_lat_rad = (self.points_long_lat[['long', 'lat']] * PI / 180).to_numpy()

        self.l0 = np.median(self.points_long_lat_rad['lat'])  # median latitude
        self.points_x_y = self.points_long_lat_rad.copy()
        self.points_x_y['long'] = R * self.points_x_y['long'] * np.cos(self.l0)
        self.points_x_y['lat'] = R * self.points_x_y['lat']

        print(self.points_x_y)


        link_points = [Point(p['id'],[p['long'],p['lat']]) for i,p in self.points_x_y.loc[self.points_x_y['red'] == "LINK"].iterrows()]
        banelco_points = [Point(p['id'],[p['long'],p['lat']]) for i,p in self.points_x_y.loc[self.points_x_y['red'] == "BANELCO"].iterrows()]

        print("ALL POINTS: ")
        print("LINK")
        print([p.ID for p in link_points])
        print("BANELCO")
        print([p.ID for p in banelco_points])


        self.kd_link = make_kdtree(link_points, axis=0)
        self.kd_banelco = make_kdtree(banelco_points, axis=0)

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
        r=pd.DataFrame({'id':results}).merge(self.points_long_lat)
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
