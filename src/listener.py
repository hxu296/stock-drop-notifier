from telegram_bots.sender import Sender
from parsers.bestbuy_parser import BestbuyParser
from parsers.newegg_parser import NeweggParser
from datetime import datetime
from datetime import timedelta
import time
import requests
import os
import yaml
import argparse
import logging
import urllib.parse

class Listener:
    
    def __init__(self, path_to_config):
        self.start_time = time.time()
        self.config = self.load_config(path_to_config)
        path_to_telegram_config = self.config['path_to_telegram_config']
        self.sender = Sender(path_to_telegram_config)
        self.chat_id = self.config['chat_id']
        self.receivers = self.config['receivers']
        self.search_words = self.config['search_words']
        self.search_words = [word.lower() for word in self.search_words]
        self.forbidden_words = self.config['forbidden_words'] 
        self.forbidden_words = [word.lower() for word in self.forbidden_words]
        self.price_ceiling = self.config['price_ceiling']
        self.rest_time = self.config['rest_time']
        self.request_frequency = self.config['request_frequency']
        self.update_interval = self.config['update_interval']
        self.needs_update = True
        self.platform = self.config['platform']
        self.parser = self.get_parser()
        self.name = self.platform + ''.join('[{}]'.format(urllib.parse.quote_plus(word)) for word in self.search_words)
        self.get_page_time = time.time()
        self.product_urls = set()
        self.prev_in_stock = set()
        self.curr_in_stock = set()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        self.load_logger()

        initial_msg = '{} bot starts running'.format(self.name)
        if len(self.receivers) > 1:
            initial_msg = 'shared ' + initial_msg
        self.send_msg(initial_msg)

    def get_parser(self):
        if self.platform == 'newegg':
            return NeweggParser()
        elif self.platform == 'bestbuy':
            return BestbuyParser()
        else:
            return None

    def load_logger(self):
        path_to_log_dir = 'log/listener_log/user_{}'.format(self.chat_id)
        if not os.path.exists(path_to_log_dir):
            os.makedirs(path_to_log_dir)
        path_to_log = '{}/{}.log'.format(path_to_log_dir, self.name)
        # create file if not exist, append if exist
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO, filename=path_to_log, filemode='a')

    def load_config(self, path_to_config):
        with open(path_to_config, 'r') as handler:
            config = yaml.full_load(handler)
        return config

    def update_url_list(self):
        run_hrs, _ , _ = self.runtime()
        self.needs_update = self.needs_update or run_hrs % self.update_interval != 0
        if self.needs_update and run_hrs % self.update_interval == 0:
            self.generate_url()
            self.needs_update = False

    def get_rest_time(self):
        curr_time = datetime.now()
        rest_start = curr_time.replace(hour=self.rest_time[0], minute=0, second=0, microsecond=0)
        rest_end = curr_time.replace(hour=self.rest_time[1], minute=0, second=0, microsecond=0)
        if self.rest_time[0] > self.rest_time[1]:
            rest_end = rest_end + timedelta(days = 1)
        if curr_time > rest_start and curr_time < rest_end:
            logging.info('listener will sleep until {}.'.format(rest_end.time()))
            rest_time = (rest_end - curr_time).total_seconds()
        else:
            rest_time = 0
        return rest_time

    def generate_url(self):
        self.product_urls = set()
        # generate product urls for each search word
        for word in self.search_words:
            # get product index urls
            search_url = self.parser.get_search_url(word)
            product_index_urls = self.parser.get_product_index_urls(search_url, self.get_page(search_url))
            # get product urls
            for product_index_url in product_index_urls:
                self.product_urls.update(self.parser.get_product_urls(self.get_page(product_index_url)))
        logging.info('generated {} urls'.format(len(self.product_urls)))

    def scan_url(self):
        # iterate through self.product_url list
        bad_urls = set()
        for product_url in self.product_urls:
            try:
                product_page = self.get_page(product_url)
                # get name, dealer, price, and stock info from product page
                name = self.parser.get_name(product_url, product_page).lower()
                dealer = self.parser.get_dealer(product_url, product_page)
                price = self.parser.get_price(product_url, product_page)
                is_in_stock = self.parser.get_inventory(product_url, product_page)
                logging.debug('scan result:\nname: {}\ndealer: {}\nprice: {}\nin_stock: {}\nurl: {}'.format(
                    name, dealer, price, is_in_stock, product_url
                ))
                # check whether product's name is valid
                name_is_valid = True
                for word in self.forbidden_words:
                    if word in name.split():
                        name_is_valid = False
                        break
                # send stock and update curr_in_stock
                if price <= self.price_ceiling and name_is_valid:
                    product_info = (product_url, price, dealer)
                    logging.critical(self.prev_in_stock)
                    logging.critical('is_in_stock:'+str(is_in_stock))
                    logging.critical('in prev_in_stock:' + str(product_info in self.prev_in_stock))
                    if is_in_stock and product_info in self.prev_in_stock:
                        self.curr_in_stock.add(product_info)
                    elif is_in_stock and product_info not in self.prev_in_stock:
                        self.send_new_stock(product_info)
                        self.curr_in_stock.add(product_info)
                    elif not is_in_stock and product_info in self.prev_in_stock:
                        self.send_dead_stock(product_info)
                    elif not is_in_stock and product_info not in self.prev_in_stock:
                        pass
                else:
                    logging.info('remove invalid url: {}'.format(product_url))
                    bad_urls.add(product_url)
            except Exception:
                # if this url causes an exception, append it to bad_urls
                logging.error('remove erroneous url: {}'.format(product_url))
                bad_urls.add(product_url)
        # remove all urls in bad_urls from self.product_urls
        if len(bad_urls) != 0:
            for bad_url in bad_urls:
                self.product_urls.remove(bad_url)
        # update prev_in_stock and curr_in_stock
        self.prev_in_stock = self.curr_in_stock
        self.curr_in_stock = set()
        
    def get_page(self, url):
        try:
            # control frequency
            duration = time.time() - self.get_page_time
            time.sleep(max(1/self.request_frequency - duration, 0))
            self.get_page_time = time.time()
            # get page from request
            req = requests.get(url, headers=self.headers, timeout=5)
            page = req.text
            logging.debug('got page from {}'.format(url))
            return page
        except Exception as e:
            # keep refreshing until a successful connection is established
            logging.error('connection error, keep refreshing. error message: {}'.format(e))
            return self.get_page(url)

    def time(self):
        return time.time() - self.start_time
    
    def runtime(self):
        run_time = self.time()
        run_secs = int(run_time % 60)
        run_mins = int((run_time % 3600) / 60)
        run_hrs = int(run_time / 3600)
        return run_hrs, run_mins, run_secs

    def send_new_stock(self, product_info):
        # send new stock available
        url, price, dealer = product_info
        msg = 'Stock Refilled!\nDealer:{}\nPrice:{}\nURL:{}'.format(dealer, price, url)
        self.send_msg(msg)

    def send_dead_stock(self, product_info):
        # send stock that was previously available, but no longer
        url, price, dealer = product_info
        msg = 'Below product is no longer available.\nDealer:{}\nPrice:{}\nURL:{}'.format(dealer, price, url)
        self.send_msg(msg)

    def send_msg(self, msg):
        for receiver in self.receivers:
            self.sender.send_message(msg, receiver)
            logging.info('sent msg to {}: {}'.format(receiver, msg))
    
    def run(self):
        try:
            while True:
                # update the url list
                self.update_url_list()
                logging.info('current url list contains {} urls.'.format(len(self.product_urls)))
                # terminate this listener if there are no urls left
                if len(self.product_urls) == 0:
                    self.send_msg('url list to listen is empty. {} bot stops working.'.format(self.name))
                    break	
                # take a rest
                time.sleep(self.get_rest_time())
                # continue to scan
                self.scan_url()
        except Exception as e:
                # an unexpected exception occurred, notify the user and terminate this process
                error_msg = 'AN INTERNAL ERROR OCCURED. {} bot ABORTS.\nERROR MSG: {}'.format(
                self.name, str(e))
                self.send_msg(error_msg)
                logging.critical(error_msg)

def main():
    parser = argparse.ArgumentParser(description='fire up a listener with the filter specified in config')
    parser.add_argument('--config', type=str, help='config file path')
    args = parser.parse_args()
    config = args.config
    listener = Listener(config)
    listener.run()

if __name__ == '__main__':
    main()
