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
