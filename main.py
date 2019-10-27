import json

import requests

token = "932440048:AAEJBx6vBq2A0fef5I-7OGEH6_25i1IIWI0"
bot_url = "https://api.telegram.org/bot" + token

last_update = 0

command_history = {}
api_key = '7sopi7Ekw99TV5rYxGXrzXIkq9dOZTAL'


def handle_msg(msg):
    print('message: ', msg)
    if 'location' in msg:
        location = msg['location']
        x = requests.post(bot_url + "/sendMessage", {'chat_id': msg['chat']['id'],
                                                     'text': 'Your location is \'{},{}\''.format(
                                                         location['latitude'],
                                                         location['latitude']),
                                                     'reply_markup': json.dumps({'remove_keyboard': True})})
        locations = '{},{}|marker-start|'.format(location['latitude'], location['longitude'])
        requests.post(bot_url + "/sendPhoto", {'chat_id': msg['chat']['id'],
                                               'photo': 'https://www.mapquestapi.com/staticmap/v5/map?locations={}&zoom=16&size=600,400@2x&key={}'.format(
                                                   locations,
                                                   api_key)})
        print("response: ", x.json())
    if 'text' in msg:
        requests.post(bot_url + "/sendMessage", {'chat_id': msg['chat']['id'],
                                                 'text': 'You said \'{}\''.format(msg['text'])})
        if 'entities' not in msg:
            requests.post(bot_url + "/sendMessage", {'chat_id': msg['chat']['id'],
                                                     'text': 'Sorry, just send a command /link, /banelco'})
        else:
            entities = msg['entities']
            if len(entities) != 1:
                requests.post(bot_url + "/sendMessage", {'chat_id': msg['chat']['id'],
                                                         'text': 'More than one entity: Sorry, just send a command /link, /banelco'})
            else:
                entity = entities[0]
                if entity['type'] != "bot_command":
                    requests.post(bot_url + "/sendMessage", {'chat_id': msg['chat']['id'],
                                                             'text': 'Not a command: Sorry, just send a command /link, /banelco'})
                else:
                    command = msg['text'][entity['offset']:entity['offset'] + entity['length']]
                    # requests.post(bot_url + "/sendMessage", {'chat_id': msg['chat']['id'],
                    #                                          'text': 'Received command' + command})
                    # requests.post(bot_url + "/sendPhoto", {'chat_id': msg['chat']['id'],
                    #                                        'photo': 'https://source.unsplash.com/random/600x600'})
                    x = requests.post(bot_url + "/sendMessage",
                                      {'chat_id': msg['chat']['id'], 'text': "Please send your location",
                                       'reply_markup': json.dumps({
                                           'keyboard': [[{'text': 'Send location', "request_location": True}]],
                                           "one_time_keyboard": True, "resize_keyboard": True})})
                    print("result: ", x.json())


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
