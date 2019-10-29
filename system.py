import pandas as pd
from kdtree import *
import threading
import time

from tinydb import TinyDB, Query

PI = 3.14159265
R = 6371000  # Earth radius in meters
N = 10  # number of initial available uses


class System:
    def reset_uses(self):
        updated = False  # this is to prevent updating more than once at 08:xx hs
        while True:
            now = time.localtime()
            if now.tm_hour == 8 and now.tm_wday < 5 and not updated:
                self.lock.acquire()
                print("#################### RESETTING USES at ", now)
                # self.uses = {id:N for id in self.points_x_y['id']}
                self.uses_db.update({'uses': N})
                for p in self.map_id_to_point.values():
                    p.active = True
                self.lock.release()
                print(self.uses)
                updated = True
            else:
                updated = False
            time.sleep(60)

    def __init__(self):

        self.lock = threading.Lock()
        reset_thread = threading.Thread(target=self.reset_uses)

        self.points_long_lat = pd.read_csv("cajeros-automaticos.csv")
        self.points_long_lat_rad = self.points_long_lat.copy()  # deep copy to keep original intact
        self.points_long_lat_rad[['long', 'lat']] = self.points_long_lat_rad[['long', 'lat']] * PI / 180
        # self.points_long_lat_rad = (self.points_long_lat[['long', 'lat']] * PI / 180).to_numpy()

        self.l0 = np.median(self.points_long_lat_rad['lat'])  # median latitude
        self.points_x_y = self.points_long_lat_rad.copy()
        self.points_x_y['long'] = R * self.points_x_y['long'] * np.cos(self.l0)
        self.points_x_y['lat'] = R * self.points_x_y['lat']
        # self.uses = {id:N for id in self.points_x_y['id']}
        self.map_id_to_point = {p['id']: Point(p['id'], [p['long'], p['lat']], True) for i, p in
                                self.points_x_y.iterrows()}
        self.uses_db = TinyDB("uses.json")
        results = self.uses_db.search(Query())
        print("DATABASE RESULTS: ", results)
        if results == []:
            # empty database, initialize
            self.uses_db.insert_multiple({'id': id, 'uses': N} for id in self.points_x_y['id'])
            for p in self.map_id_to_point.values():
                p.active = True
        else:
            for r in results:
                self.map_id_to_point[r['id']].active = r['uses'] != 0

        # print("USES:" ,self.uses)
        # print(self.points_x_y)

        reset_thread.start()

        link_points = [self.map_id_to_point[p['id']] for i, p in
                       self.points_x_y.loc[self.points_x_y['red'] == "LINK"].iterrows()]
        banelco_points = [self.map_id_to_point[p['id']] for i, p in
                          self.points_x_y.loc[self.points_x_y['red'] == "BANELCO"].iterrows()]

        # print("ALL POINTS: ")
        # print("LINK")
        # print([p.ID for p in link_points])
        # print("BANELCO")
        # print([p.ID for p in banelco_points])

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

        self.lock.acquire()

        results = search_closest_kdtree(kd_search, q, 3)
        l = []
        # keep only the places which are within 500m
        for r in results:
            if r['distance'] < 500:
                l.append(r)
        results = l

        # print("RESULTSIII: ", results)
        ids = [p['point'].ID for p in results]
        r = pd.DataFrame({'id': ids}).merge(self.points_long_lat)
        self.simulate_use(ids)

        self.lock.release()

        # print(self.uses)
        return r, {p['point'].ID: p['distance'] for p in results}

    def simulate_use(self, r):
        # given a list of point ids, choose one of them according to the following distribution
        if len(r) == 0:
            # no results
            return
        if len(r) == 1:
            # only one result within 500m with available uses, choose it 100% of the cases
            c = 0
        else:
            x = np.random.rand()
            if len(r) == 2:
                # two results within 500m with available uses, choose 1st 70% and 2nd 30%
                if x < 0.7:
                    c = 0
                else:
                    c = 1
            elif len(r) == 3:
                # three results withing 500m with available uses, choose 70% closest, 20% 2nd closest 10% 3d closest
                if x < 0.7:
                    c = 0
                if x > 0.7 and x < 0.9:
                    c = 1
                if x > 0.9:
                    c = 2
        print("chosen id: ", r[c])
        u = self.uses_db.search(Query().id == r[c])[0]['uses']  # current number of available uses
        print("******************USES LEFT: ", u - 1)
        self.uses_db.update({'uses': u - 1}, Query().id == r[c])  # decrease number of available uses by 1
        if u - 1 == 0:
            # if there are no more available uses, don't consider this point in further searches, until next reset
            self.map_id_to_point[r[c]].active = False


if __name__ == '__main__':

    s = System()
    result = s.search_nearest(-34, -58, 'LINK')
    print(result)
    l = ["{}".format(r['ubicacion']) for i, r in result.iterrows()]
    print(l)
    for i, r in result.iterrows():
        plt.scatter(r['long'], r['lat'], color="r")
    plt.scatter(-58, -34, color="g")
    plt.show()
