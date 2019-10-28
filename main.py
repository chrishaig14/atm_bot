import json

import requests

from system import System

token = "932440048:AAEJBx6vBq2A0fef5I-7OGEH6_25i1IIWI0"
bot_url = "https://api.telegram.org/bot" + token

last_update = 0

command_history = {}
api_key = '7sopi7Ekw99TV5rYxGXrzXIkq9dOZTAL'

s = System()


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
        results = s.search_nearest(start[0], start[1], "LINK")

        print("RESULTS: ", results)

        locations = [[l['lat'], l['long']] for i, l in results.iterrows()]
        map_url = make_map_url(start, locations)
        print("MAP URL: ", map_url)
        x = requests.post(bot_url + "/sendPhoto", {'chat_id': msg['chat']['id'],
                                                   'photo': map_url,
                                                   'reply_markup': json.dumps({'remove_keyboard': True})})
        print("response: ", x.json())
        msg_text = ""
        n = 0
        for i,l in results.iterrows():
            msg_text += str(n+1) + ") " + l['banco'] + " - " + l["ubicacion"] + "\n"
            n += 1

        x = requests.post(bot_url+"/sendMessage",{"chat_id":msg["chat"]["id"],"text":msg_text})
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
