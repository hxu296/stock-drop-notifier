from bs4 import BeautifulSoup as soup
import urllib.parse

class NeweggParser:

    def __init__(self):
        self.search_base_url = 'https://www.newegg.com/p/pl?d='
 
    def get_product_urls(self, product_index_page):
        # get product titles
        product_index_soup = soup(product_index_page, 'lxml')
        product_titles = product_index_soup.findAll('a', {'class':'item-title'}, href=True)
        # get product urls
        product_urls = []
        for product_title in product_titles:
            product_urls.append(product_title['href'])
        return product_urls

    def get_product_index_urls(self, search_url, search_page):
        # get max search page number
        search_soup = soup(search_page, 'lxml')
        page_num = int(search_soup.find('span', {'class':'list-tool-pagination-text'}).find(
        'strong').contents[4])
        # get product index pages 
        product_index_urls = []
        for page_index in range(1, page_num + 1):
            product_index_url = search_url + '&p={}'.format(page_index)
            product_index_urls.append(product_index_url)
        return product_index_urls

    def get_search_url(self, search_str):
        search_url = self.search_base_url + urllib.parse.quote_plus(search_str)
        return search_url

    def get_name(self, product_url, product_page):
        product_soup = soup(product_page, 'lxml')
        name = 'unknown name'
        if self.is_combo_deal(product_url):
            name = product_soup.find('span', {'itemprop':'name'}).contents[0]
        else:
            name = product_soup.find('h1', {'class':'product-title'}).contents[0]
        return name

    def get_dealer(self, product_url, product_page):
        product_soup = soup(product_page, 'lxml')
        if self.is_combo_deal(product_url):
            dealer = 'Combo Deal'
        else:
            pane = product_soup.find('div', {'class':'product-pane'})
            dealer = pane.find('div', {'class':'product-seller'}).find('strong').contents[0]
        return dealer

    def get_price(self, product_url, product_page):
        product_soup = soup(product_page, 'lxml')
        if self.is_combo_deal(product_url):
            pane = product_soup.find('tr', {'class':'grand_total'})
            price_str = pane.find('td', {'class':'price'}).contents[0]
            price_str = price_str.replace('$', '').replace(',', '')
            price = float(price_str)
        else:
            pane = product_soup.find('div', {'class':'product-pane'})
            price_str = pane.find('li', {'class':'price-current'}).find('strong').contents[0]
            price_str = price_str.replace('$', '').replace(',', '')
            price = float(price_str)
        return price

    def get_inventory(self, product_url, product_page):
        product_soup = soup(product_page, 'lxml')
        if self.is_combo_deal(product_url):
            inventory = product_soup.find('p', {'class':'note'})   
        else:
            inventory = product_soup.find('div', {'class':'product-inventory'}).find('strong')
        in_stock = len(inventory) == 1 and 'out of stock' not in inventory.contents[0].lower()
        return in_stock

    def is_combo_deal(self, product_url):
        return 'combo' in product_url.lower()





         


