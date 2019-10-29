import pandas as pd
from kdtree import *

from tinydb import TinyDB, Query

PI = 3.14159265
R = 6371000  # Earth radius in meters
N = 1000  # number of initial available withdrawals
MAX_DISTANCE = 500  # max distance in meters
DB_FILE = "cajeros-automaticos.csv"


class SearchSystem:

    def __init__(self):
        self.points_long_lat = None  # original data
        self.l0 = None  # median latitude
        self.points_x_y = None  # points with x, y coords
        self.map_id_to_point = None  # maps id -> Point for kd trees
        self.load_points()

        self.available_db = None  # db which maps id -> # available withdrawals
        self.initialize_available_db()

        self.kd_link = None  # kd tree for "LINK"
        self.kd_banelco = None  # kd tree for "BANELCO
        self.make_kdtrees()

    def load_points(self):
        self.points_long_lat = pd.read_csv(DB_FILE)

        points_long_lat_rad = self.points_long_lat.copy()  # convert degrees to radians
        points_long_lat_rad[['long', 'lat']] = points_long_lat_rad[['long', 'lat']] * PI / 180

        # equirectangular projection
        self.l0 = np.median(points_long_lat_rad['lat'])  # median latitude
        self.points_x_y = points_long_lat_rad
        self.points_x_y['long'] = R * self.points_x_y['long'] * np.cos(self.l0)
        self.points_x_y['lat'] = R * self.points_x_y['lat']

        # maps id to Point
        self.map_id_to_point = {p['id']: Point(p['id'], [p['long'], p['lat']], True) for i, p in
                                self.points_x_y.iterrows()}

    def initialize_available_db(self):
        self.available_db = TinyDB("available.json")
        results = self.available_db.search(Query())

        if results == []:
            # empty database, initialize
            print("EMPTY 'available' DATABASE, INITIALIZING")
            self.available_db.insert_multiple({'id': id, 'available': N} for id in self.points_x_y['id'])
            for p in self.map_id_to_point.values():
                p.active = True
        else:
            print("'available' DATABASE FOUND, LOADING")
            for r in results:
                self.map_id_to_point[r['id']].active = r['available'] != 0

    def make_kdtrees(self):
        link_points = [self.map_id_to_point[p['id']] for i, p in
                       self.points_x_y.loc[self.points_x_y['red'] == "LINK"].iterrows()]
        banelco_points = [self.map_id_to_point[p['id']] for i, p in
                          self.points_x_y.loc[self.points_x_y['red'] == "BANELCO"].iterrows()]

        self.kd_link = make_kdtree(link_points, axis=0)
        self.kd_banelco = make_kdtree(banelco_points, axis=0)

    def search_nearest(self, lat, long, net):
        kd_search = None

        # select kd-tree to use
        if net == "LINK":
            kd_search = self.kd_link
        elif net == "BANELCO":
            kd_search = self.kd_banelco

        # convert query point to x, y
        q = [long * PI / 180, lat * PI / 180]
        q[0] = R * q[0] * np.cos(self.l0)
        q[1] = R * q[1]

        # perform search
        results = search_closest_kdtree(kd_search, q, 3)
        within_distance = []
        # keep only the places which are within 500m
        for r in results:
            if r['distance'] < MAX_DISTANCE:
                within_distance.append(r)
        results = within_distance
        print("SEARCH REUSLTS:")
        for r in results:
            print("ID {} : DISTANCE {}m".format(r['point'], r['distance']))

        # simulate user choice
        ids = [p['point'].ID for p in results]
        self.simulate_choice(ids)

        # get results info
        info = pd.DataFrame({'id': ids}).merge(self.points_long_lat)

        # return points along with distance
        return info, {p['point'].ID: p['distance'] for p in results}

    def simulate_choice(self, result_ids):
        # given a list of point ids, choose one of them according to the following distribution
        if len(result_ids) == 0:
            # no results
            return
        c = 0
        if len(result_ids) == 1:
            # only one result within 500m with available uses, choose it 100% of the cases
            c = 0
        else:
            x = np.random.rand()
            if len(result_ids) == 2:
                # two results within 500m with available uses, choose 1st 70% and 2nd 30%
                if x < 0.7:
                    c = 0
                else:
                    c = 1
            elif len(result_ids) == 3:
                # three results withing 500m with available uses, choose 70% closest, 20% 2nd closest 10% 3d closest
                if x < 0.7:
                    c = 0
                if 0.7 < x < 0.9:
                    c = 1
                if x > 0.9:
                    c = 2
        chosen_id = result_ids[c]
        available = self.available_db.search(Query().id == chosen_id)[0][
            'available']  # current number of available uses
        new_available = available - 1
        print("CHOSEN ID {} : {} AVAILABLE".format(chosen_id, new_available))
        self.available_db.update({'available': new_available},
                                 Query().id == chosen_id)  # decrease number of available uses by 1
        if new_available == 0:
            # if there are no more available uses, don't consider this point in further searches, until next reset
            self.map_id_to_point[chosen_id].active = False

    def reset_available(self):
        print("RESETTING 'available'")
        self.available_db.update({'available': N})
        for p in self.map_id_to_point.values():
            p.active = True
