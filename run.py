from src.telegram_bots.server import Server
import argparse
import yaml
import re

def get_token():
    token = input("paste your Telegram bot token and press enter: ")
    token = token.strip()
    if not bool(re.search("[0-9]{8,10}:[a-zA-Z0-9_-]{35}", token)):
        print("run.py: invalid Telegram bot token")
        quit()
    return token

def rewrite_token(token, path_to_config):
    with open(path_to_config, 'r') as handler:
        config = yaml.full_load(handler)
    config['token'] = token
    with open(path_to_config, 'w') as handler:
        yaml.dump(config, handler)

def main():
    path_to_config = 'config/telegram_config_public.yaml'
    parser = argparse.ArgumentParser(usage='python run.py [-m]', description='Start Telegram bot service')
    parser.add_argument('-m', action='store_true', help='rewrite current Telegram bot token')
    args = parser.parse_args()
    if args.m:
        token = get_token()
        rewrite_token(token, path_to_config)
    server = Server(path_to_config)
    print('server starts running!')
    server.run()

if __name__ == "__main__":
    main()

