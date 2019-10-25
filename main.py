import requests

token = "932440048:AAEJBx6vBq2A0fef5I-7OGEH6_25i1IIWI0"
bot_url = "https://api.telegram.org/bot" + token

last_update = 0

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
        print('message: ', msg)
        requests.post(bot_url + "/sendMessage", {'chat_id': msg['message']['chat']['id'],
                                                 'text': 'You said \'{}\''.format(msg['message']['text'])})
        if 'entities' not in msg['message']:
            requests.post(bot_url + "/sendMessage", {'chat_id': msg['message']['chat']['id'],
                                                     'text': 'Sorry, just send a command /link, /banelco'})
        else:
            entities = msg['message']['entities']
            if len(entities) != 1:
                requests.post(bot_url + "/sendMessage", {'chat_id': msg['message']['chat']['id'],
                                                         'text': 'More than one entity: Sorry, just send a command /link, /banelco'})
            else:
                entity = entities[0]
                if entity['type'] != "bot_command":
                    requests.post(bot_url + "/sendMessage", {'chat_id': msg['message']['chat']['id'],
                                                             'text': 'Not a command: Sorry, just send a command /link, /banelco'})
                else:
                    command = msg['message']['text'][entity['offset']:entity['offset'] + entity['length']]
                    requests.post(bot_url + "/sendMessage", {'chat_id': msg['message']['chat']['id'],
                                                             'text': 'Received command' + command})
