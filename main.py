import json
import threading
import schedule
import requests

from searchsystem import SearchSystem

TOKEN = "932440048:AAEJBx6vBq2A0fef5I-7OGEH6_25i1IIWI0"  # Telegram bot API token
BOT_URL = "https://api.telegram.org/bot" + TOKEN  # bot API base url

commands = ["LINK", "BANELCO"]

MSG_INFO = 'Enviar comando /link o /banelco'
MSG_REQUEST_LOCATION = "Por favor, enviar su ubicación"
MSG_NO_RESULTS = "No hay cajeros disponibles"
MSG_RESULTS = "Cajeros de la red "
MSG_SEND_LOCATION = 'Enviar ubicación'


def make_map_url(start, locations):
    # make MapQuest url to generate map from start (user location) and locations (search results)

    API_KEY = '7sopi7Ekw99TV5rYxGXrzXIkq9dOZTAL'  # MapQuest API key
    MAP_URL = 'https://www.mapquestapi.com/staticmap/v5/map?locations={}||{}&zoom=16&size=600,400@2x&key={}'

    start = '{},{}|marker-start'.format(start[0], start[1])
    ls = ""
    for i, l in enumerate(locations):
        ls += "{},{}|marker-{}||".format(l[0], l[1], i + 1)
    return MAP_URL.format(start, ls, API_KEY)


def handle_text_msg(msg, command_history):
    command = msg["text"][1:].upper()  # remove fwd slash
    if command in commands:
        command_history[msg["from"]["id"]] = command  # remember command for when location arrives
        # show keyboard with single button to send location
        reply_markup = json.dumps({
            'keyboard': [[{'text': MSG_SEND_LOCATION, "request_location": True}]],
            "one_time_keyboard": True, "resize_keyboard": True})
        msg_obj = {'chat_id': msg['chat']['id'], 'text': MSG_REQUEST_LOCATION, 'reply_markup': reply_markup}
        async_post(BOT_URL + "/sendMessage", msg_obj, None)
    else:
        # unknown command, send ingo
        async_post(BOT_URL + "/sendMessage", {'chat_id': msg['chat']['id'], 'text': MSG_INFO}, None)


def post(url, data, callback):
    # when we get the response, run the callback
    x = requests.post(url, data)
    if callback:
        callback(x)


def async_post(url, data, callback):
    # this is a very simple way to make non blocking requests. we could also use e.g. aiohttp
    th = threading.Thread(target=post, args=(url, data, callback))
    th.start()


def handle_location_msg(msg, command_history, search_sys):
    if msg["from"]["id"] not in command_history:
        # we don't have the command for this user, send info instead
        async_post(BOT_URL + "/sendMessage", {'chat_id': msg['chat']['id'],
                                              'text': MSG_INFO}, None)
        return
    command = command_history[msg["from"]["id"]]  # command the user sent, before sending his location
    location = msg['location']
    start = [location['latitude'], location['longitude']]
    results = search_sys.search_nearest(start[0], start[1], command)

    if len(results[0]) == 0:
        # no results
        async_post(BOT_URL + "/sendMessage", {"chat_id": msg["chat"]["id"], "text": MSG_NO_RESULTS}, None)
        return

    locations = [[l['lat'], l['long']] for i, l in results[0].iterrows()]
    map_url = make_map_url(start, locations)

    msg_text = MSG_RESULTS + command + "\n"
    n = 0
    for i, l in results[0].iterrows():
        msg_text += "{})\nBanco: {}\nDirección: {}\nDistancia: {}m\n".format(i + 1, l['banco'], l['ubicacion'],
                                                                             int(results[1][l['id']]))
        n += 1
    async_post(BOT_URL + "/sendPhoto", {'chat_id': msg['chat']['id'],
                                        'photo': map_url, 'caption': msg_text,
                                        'reply_markup': json.dumps(
                                            {'remove_keyboard': True})}, None)
    del command_history[msg["from"]["id"]]  # we've just answered this command, so delete it


def handle_msg(msg, command_history, search_sys):
    if 'location' in msg:
        # message contains location, no text
        handle_location_msg(msg, command_history, search_sys)
    if 'text' in msg:
        # text message
        handle_text_msg(msg, command_history)


def main():
    last_update = 0  # latest update id received

    command_history = {}  # maps user id to last command

    search_sys = SearchSystem()

    # set up scheduler to reset available at specified times

    schedule.every().monday.at("08:00").do(search_sys.reset_available)
    schedule.every().tuesday.at("08:00").do(search_sys.reset_available)
    schedule.every().wednesday.at("08:00").do(search_sys.reset_available)
    schedule.every().thursday.at("08:00").do(search_sys.reset_available)
    schedule.every().friday.at("08:00").do(search_sys.reset_available)

    while True:
        schedule.run_pending()  # reset available uses if it's time
        params = {'timeout': 60, 'offset': last_update + 1}
        response = requests.post(BOT_URL + "/getUpdates", params)  # here we have to block and wait for updates
        response_json = response.json()
        if len(response_json['result']) == 0:
            # request timed out, repeat
            print("TIMEOUT: NO NEW MESSAGES")
            continue
        last_update = response_json['result'][-1][
            'update_id']  # we need this to acknowledge these updates in the next /getUpdates request
        for msg in response_json['result']:
            handle_msg(msg['message'], command_history, search_sys)


if __name__ == '__main__':
    main()
