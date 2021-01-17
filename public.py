from src.telegram_bots.server import Server

server = Server('config/telegram_config_public.yaml')
server.run()


