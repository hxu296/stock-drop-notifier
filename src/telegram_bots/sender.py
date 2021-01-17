import requests
import json
import yaml

class Sender:

    def __init__(self, path_to_config):
        self.config = self.load_config(path_to_config)
        self.token = self.config['token']
        self.base = 'https://api.telegram.org/bot{}/'.format(self.token)
 
    def send_message(self, msg, chat_id):
        url = self.base + 'sendMessage?text={}&chat_id={}'.format(msg, chat_id)
        if msg is not None: 
                requests.get(url)

    def load_config(self, path_to_config):
        with open(path_to_config, 'r') as handler:
            config = yaml.full_load(handler)
        return config
