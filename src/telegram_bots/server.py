from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (Updater,
                          CommandHandler,
                          PrefixHandler,
                          MessageHandler,
                          Filters,
                          ConversationHandler,
                          CallbackContext)
import yaml
import logging
import os
import signal
import subprocess


class Server:

    def __init__(self, path_to_config):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO, filename='log/server_log/server.log')
        self.config = self.load_config(path_to_config)
        self.token = self.config['token']
        path_to_reply_dict = self.config['path_to_telegram_reply_dict']
        self.reply_dict = self.load_reply_dict(path_to_reply_dict)
        self.dispatcher = {'search': self.search,
                           'forbid': self.forbid,
                           'price': self.price,
                           'rest': self.rest,
                           'freq': self.freq,
                           'refresh': self.refresh}
        self.filter_keys = {
            'search': 'search_words',
            'forbid': 'forbidden_words',
            'price': 'price_ceiling',
            'freq': 'request_frequency',
            'refresh': 'update_interval',
            'rest': 'rest_time'
        }

    def load_config(self, path_to_config):
        with open(path_to_config, 'r') as handler:
            config = yaml.full_load(handler)
        return config

    def load_reply_dict(self, path_to_reply_dict):
        with open(path_to_reply_dict, 'r') as handler:
            reply_dict = yaml.full_load(handler)
        return reply_dict

    def start(self, update, context):
        chat_id = update.effective_chat.id
        reply = self.reply_dict['start']
        context.bot.send_message(chat_id=chat_id, text=reply)

    def help(self, update, context):
        chat_id = update.effective_chat.id
        reply = self.reply_dict['help']
        context.bot.send_message(chat_id=chat_id, text=reply)

    def list_start(self, update, context):
        chat_id = update.effective_chat.id
        reply = self.reply_dict['list_start']
        reply_keyboard = [['filter', 'notifier']]
        context.bot.send_message(
            chat_id=chat_id,
            text=reply,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return 'list_choice'

    def list_choice(self, update, context):
        chat_id = update.effective_chat.id
        user_data = context.user_data
        choice = update.message.text
        context.user_data['choice'] = choice
        if choice == 'notifier':
            if 'notifiers' in user_data and user_data['notifiers']:
                notifiers = user_data['notifiers']
                reply = self.reply_dict['list_choice']
                reply_keyboard = [[notifier['id'] for notifier in notifiers.values()]]
                context.bot.send_message(chat_id=chat_id,
                                        text=reply,
                                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
                return 'list_notifier'
            else:
                reply = self.reply_dict['list_empty']
                context.bot.send_message(chat_id=chat_id, text=reply)
                return ConversationHandler.END
        elif choice == 'filter':
            if 'filter' not in user_data:
                user_data['filter'] = self.new_filter()
            reply = '{}\n{}'.format(self.reply_dict['list_filter'], str(user_data['filter']))
            context.bot.send_message(chat_id=chat_id, text=reply)
            return ConversationHandler.END

    def list_notifier(self, update, context):
        chat_id = update.effective_chat.id
        user_data = context.user_data
        pid = int(update.message.text)
        config = user_data['notifiers'][pid]
        reply = '{}\n{}'.format(self.reply_dict['list_notifier'], str(config))
        context.bot.send_message(chat_id=chat_id, text=reply)
        return ConversationHandler.END

    def add(self, update, context):
        chat_id = update.effective_chat.id
        user_data = context.user_data
        if 'notifiers' not in user_data:
            user_data['notifiers'] = {}
        if 'filter' not in user_data:
            user_data['filter'] = self.new_filter()
        try:
            curr_filter = user_data['filter']
            if any([value is None for value in curr_filter.values()]):
                raise TypeError(self.reply_dict['add_error'])
            curr_filter['chat_id'] = chat_id
            curr_filter['path_to_telegram_config'] = self.config['path_to_telegram_config']
            path_to_listener_config = self.dump_listener_config(curr_filter)
            pid = self.start_listener(path_to_listener_config)
            del curr_filter['chat_id']
            del curr_filter['path_to_telegram_config']
            user_data['notifiers'][pid] = curr_filter
            user_data['notifiers'][pid]['id'] = pid
            reply = '{}\nnotifier id: {}'.format(self.reply_dict['add_success'], pid)
            context.bot.send_message(chat_id=chat_id, text=reply)
        except Exception as e:
            reply = '{}\n{}'.format(self.reply_dict['add_failure'], e.args[0])
            context.bot.send_message(chat_id=chat_id, text=reply)

    def rm(self, update, context):
        chat_id = update.effective_chat.id
        user_data = context.user_data
        try:
            if any([not arg.isnumeric() for arg in context.args]):
                raise TypeError(self.reply_dict['rm_error'])
            for arg in context.args:
                pid = int(arg)
                if 'notifiers' in user_data and pid in user_data['notifiers']:
                    os.kill(pid, signal.SIGKILL)
                    del user_data['notifiers'][pid]
                else:
                    raise TypeError(self.reply_dict['rm_error'])
            reply = '{}\nnotifier {} removed.'.format(self.reply_dict['rm_success'], context.args)
            context.bot.send_message(chat_id=chat_id, text=reply)
        except Exception as e:
            reply = '{}\n{}'.format(self.reply_dict['rm_failure'], e.args[0])
            context.bot.send_message(chat_id=chat_id, text=reply)

    def search(self, args):
        return self.filter_keys['search'], args

    def forbid(self, args):
        return self.filter_keys['forbid'], args

    def price(self, args):
        if len(args) != 1:
            raise TypeError(self.reply_dict['price_error'])
        elif not args[0].isnumeric():
            raise TypeError(self.reply_dict['price_error'])

        return self.filter_keys['price'], int(args[0])

    def rest(self, args):
        if len(args) != 2:
            raise TypeError(self.reply_dict['rest_error'])
        elif not args[0].isnumeric() or not args[1].isnumeric():
            raise TypeError(self.reply_dict['rest_error'])
        elif any([int(time) < 0 or int(time) > 24 for time in args]):
            raise TypeError(self.reply_dict['rest_error'])
        return self.filter_keys['rest'], [int(time) for time in args]

    def freq(self, args):
        if len(args) != 1:
            raise TypeError(self.reply_dict['freq_error'])
        try:
            frequency = float(args[0])
        except:
            raise TypeError(self.reply_dict['freq_error'])
        if frequency > 0.3:
            raise ValueError(
                {'message': self.reply_dict['freq_warning'],
                 'filter_key': self.filter_keys['freq'], 'filter_val': frequency})
        return self.filter_keys['freq'], frequency

    def refresh(self, args):
        if len(args) != 1:
            raise TypeError(self.reply_dict['refresh_error'])
        elif not args[0].isnumeric():
            raise TypeError(self.reply_dict['refresh_error'])
        refresh = int(args[0])
        return self.filter_keys['refresh'], refresh

    def new_filter(self):
        new_filter = {self.filter_keys['freq']: self.config['default_request_frequency'],
                      self.filter_keys['refresh']: self.config['default_update_interval'],
                      self.filter_keys['rest']: self.config['default_rest_time'],
                      self.filter_keys['forbid']: self.config['default_forbidden_words'],
                      self.filter_keys['search']: None,
                      self.filter_keys['price']: None
                      }
        return new_filter

    def filter(self, update, context):
        chat_id = update.effective_chat.id
        user_data = context.user_data
        message = update.message.text
        # add filter dictionary to user_data if necessary
        if 'filter' not in user_data.keys():
            user_data['filter'] = self.new_filter()
        # parse message to determine the filter parameter to change
        filter_prompt = message.split()[0][1:]
        try:
            filter_key, filter_val = self.dispatcher[filter_prompt](context.args)
            user_data['filter'][filter_key] = filter_val
            reply = '{}\nchanged {} to {}.'.format(self.reply_dict['filter_success'], filter_key, filter_val)
            context.bot.send_message(chat_id=chat_id, text=reply)
        except TypeError as e:
            reply = '{}\n{}'.format(self.reply_dict['filter_failure'], e.args[0])
            context.bot.send_message(chat_id=chat_id, text=reply)
            pass
        except ValueError as e:
            reply = '{}\n{}'.format(self.reply_dict['filter_warning'], e.args[0]['message'])
            context.bot.send_message(chat_id=chat_id, text=reply)
            user_data['filter'][e.args[0]['filter_key']] = e.args[0]['filter_val']

    def start_listener(self, from_listener_to_config):
        pid = subprocess.Popen(['python', 'listener.py', '--config', from_listener_to_config]).pid
        return pid

    def dump_listener_config(self, config):
        chat_id = config['chat_id']
        from_listener_to_config = 'config/listener_config/user_{}.yaml'.format(chat_id)
        with open(from_listener_to_config, 'w') as handler:
            yaml.dump(config, handler)
        return from_listener_to_config

    def run(self):
        updater = Updater(token=self.token, use_context=True)
        dispatcher = updater.dispatcher

        start_handler = CommandHandler('start', self.start)
        dispatcher.add_handler(start_handler)

        help_handler = CommandHandler('help', self.help)
        dispatcher.add_handler(help_handler)

        list_handler = ConversationHandler(
            entry_points=[CommandHandler('list', self.list_start)],
            states={'list_choice':[MessageHandler(Filters.text & ~Filters.command, self.list_choice)],
                    'list_notifier':[MessageHandler(Filters.text & ~Filters.command, self.list_notifier)]},
            fallbacks=[]
        )
        dispatcher.add_handler(list_handler)

        add_handler = CommandHandler('add', self.add)
        dispatcher.add_handler(add_handler)

        rm_handler = CommandHandler('rm', self.rm)
        dispatcher.add_handler(rm_handler)

        filter_handler = PrefixHandler('!', ['search', 'forbid', 'price', 'rest', 'freq', 'refresh'], self.filter)
        dispatcher.add_handler(filter_handler)

        updater.start_polling()
        updater.idle()
