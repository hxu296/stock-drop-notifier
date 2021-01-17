from src.telegram_bots.server import Server

server = Server('config/telegram_config.yaml')
server.run()


