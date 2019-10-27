import json

import requests

token = "932440048:AAEJBx6vBq2A0fef5I-7OGEH6_25i1IIWI0"
bot_url = "https://api.telegram.org/bot" + token

last_update = 0

command_history = {}
api_key = '7sopi7Ekw99TV5rYxGXrzXIkq9dOZTAL'

###########

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

p_link = link[['lat', 'long']].to_numpy()

plt.scatter(p_link[:, 0], p_link[:, 1])
plt.show()

kd_link = make_kdtree(p_link, axis=0)
plot_points(p_link)
num = 3
q = [(xmax + xmin) / 2, (ymax + ymin) / 2]
b = search_closest_kdtree(kd_link, q, num)
b = np.array(b)


# plt.scatter(b[:, 0], b[:, 1], color='b')
# plt.scatter(q[0], q[1], color='g')
# plt.show()
##################

def make_map_url(start, locations):
    start = '{},{}|marker-start'.format(start[0], start[1])
    ls = ""
    for i, l in enumerate(locations):
        ls += "{},{}|marker-{}||".format(l[0], l[1], i + 1)

    return 'https://www.mapquestapi.com/staticmap/v5/map?locations={}||{}&zoom=16&size=600,400@2x&key={}'.format(start,
                                                                                                                 ls,
                                                                                                                 api_key)


def handle_msg(msg):
    print('message: ', msg)
    if 'location' in msg:
        location = msg['location']
        start = [location['latitude'], location['longitude']]
        locations = search_closest_kdtree(kd_link, start, 5)
        map_url = make_map_url(start, locations)
        print("MAP URL: ", map_url)
        x = requests.post(bot_url + "/sendPhoto", {'chat_id': msg['chat']['id'],
                                                   'photo': map_url,
                                                   'reply_markup': json.dumps({'remove_keyboard': True})})
        print("response: ", x.json())
    if 'text' in msg:
        requests.post(bot_url + "/sendMessage", {'chat_id': msg['chat']['id'],
                                                 'text': 'You said \'{}\''.format(msg['text'])})
        ok = False
        if 'entities' in msg:
            if len(msg['entities']) == 1:
                entity = msg['entities'][0]
                if entity['type'] == 'bot_command':
                    command = msg['text'][entity['offset']:entity['offset'] + entity['length']]
                    if command == "/link" or command == "/banelco":
                        ok = True
                        text = "Please send your location"
                        reply_markup = json.dumps({
                            'keyboard': [[{'text': 'Send location', "request_location": True}]],
                            "one_time_keyboard": True, "resize_keyboard": True})
                        msg_obj = {'chat_id': msg['chat']['id'], 'text': text, 'reply_markup': reply_markup}
                        x = requests.post(bot_url + "/sendMessage", msg_obj)
        if not ok:
            requests.post(bot_url + "/sendMessage", {'chat_id': msg['chat']['id'],
                                                     'text': 'Sorry, just send a command /link, /banelco'})


while True:
    params = {'timeout': 60, 'offset': last_update + 1}
    response = requests.post(bot_url + "/getUpdates", params)
    response_json = response.json()
    if len(response_json['result']) == 0:
        print("timeout: no new messages")
        continue
    last_update = response_json['result'][-1]['update_id']
    print("updates:")
    for msg in response_json['result']:
        handle_msg(msg['message'])
