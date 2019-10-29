import json
import requests
from system import System

TOKEN = "932440048:AAEJBx6vBq2A0fef5I-7OGEH6_25i1IIWI0"
BOT_URL = "https://api.telegram.org/bot" + TOKEN

last_update = 0

command_history = {}  # user id -> last command

API_KEY = '7sopi7Ekw99TV5rYxGXrzXIkq9dOZTAL'

MAP_URL = 'https://www.mapquestapi.com/staticmap/v5/map?locations={}||{}&zoom=16&size=600,400@2x&key={}'

s = System()


def make_map_url(start, locations):
    start = '{},{}|marker-start'.format(start[0], start[1])
    ls = ""
    for i, l in enumerate(locations):
        ls += "{},{}|marker-{}||".format(l[0], l[1], i + 1)
    return MAP_URL.format(start, ls, API_KEY)


commands = ["LINK", "BANELCO"]

MSG_INFO = 'Enviar comando /link o /banelco'
MSG_REQUEST_LOCATION = "Por favor, enviar su ubicación"
MSG_NO_RESULTS = "No hay cajeros disponibles"
MSG_RESULTS = "Cajeros de la red "
MSG_SEND_LOCATION = 'Enviar ubicación'


def handle_text_msg(msg):
    command = msg["text"][1:].upper()  # remove fwd slash
    if command in commands:
        command_history[msg["from"]["id"]] = command  # remember command for when location arrives
        reply_markup = json.dumps({
            'keyboard': [[{'text': MSG_SEND_LOCATION, "request_location": True}]],
            "one_time_keyboard": True, "resize_keyboard": True})
        msg_obj = {'chat_id': msg['chat']['id'], 'text': MSG_REQUEST_LOCATION, 'reply_markup': reply_markup}
        x = requests.post(BOT_URL + "/sendMessage", msg_obj)
    else:
        requests.post(BOT_URL + "/sendMessage", {'chat_id': msg['chat']['id'], 'text': MSG_INFO})


def handle_location_msg(msg):
    if msg["from"]["id"] not in command_history:
        requests.post(BOT_URL + "/sendMessage", {'chat_id': msg['chat']['id'],
                                                 'text': MSG_INFO})
        return
    command = command_history[msg["from"]["id"]]
    location = msg['location']
    start = [location['latitude'], location['longitude']]
    results = s.search_nearest(start[0], start[1], command)

    if len(results[0]) == 0:
        x = requests.post(BOT_URL + "/sendMessage",
                          {"chat_id": msg["chat"]["id"], "text": MSG_NO_RESULTS})
        return

    print("RESULTS: ", results)

    locations = [[l['lat'], l['long']] for i, l in results[0].iterrows()]
    map_url = make_map_url(start, locations)
    print("MAP URL: ", map_url)
    x = requests.post(BOT_URL + "/sendPhoto", {'chat_id': msg['chat']['id'],
                                               'photo': map_url,
                                               'reply_markup': json.dumps({'remove_keyboard': True})})
    print("Response: ", x.json())
    msg_text = MSG_RESULTS + command + "\n"
    n = 0
    for i, l in results[0].iterrows():
        msg_text += "{})\nBanco: {}\nDirección: {}\nDistancia: {}m\n".format(i + 1, l['banco'], l['ubicacion'],
                                                                             int(results[1][l['id']]))
        n += 1
    del command_history[msg["from"]["id"]]
    x = requests.post(BOT_URL + "/sendMessage", {"chat_id": msg["chat"]["id"], "text": msg_text})
    print("Response: ", x.json())


def handle_msg(msg):
    print('message: ', msg)
    if 'location' in msg:
        handle_location_msg(msg)
    if 'text' in msg:
        handle_text_msg(msg)


while True:
    params = {'timeout': 60, 'offset': last_update + 1}
    response = requests.post(BOT_URL + "/getUpdates", params)
    response_json = response.json()
    if len(response_json['result']) == 0:
        print("timeout: no new messages")
        continue
    last_update = response_json['result'][-1]['update_id']
    print("updates:")
    for msg in response_json['result']:
        handle_msg(msg['message'])
