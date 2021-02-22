from bs4 import BeautifulSoup as soup
import urllib.parse
import re


class BhphotoParser:

    def __init__(self):
        self.search_base_url = 'https://www.bhphotovideo.com/c/search?Ntt='
        self.product_base_url = 'https://www.bestbuy.com'

    def get_product_urls(self, product_index_page):
        # get product titles
        product_index_soup = soup(product_index_page, 'lxml')
        product_list = product_index_soup.find('ol', {'class': 'sku-item-list'})
        product_titles = product_index_soup.findAll('div', {'class': 'sku-title'})
        # get product urls
        product_urls = []
        for product_title in product_titles:
            product_urls.append(self.product_base_url + product_title.find('a', href=True)['href'])
        return product_urls

    def get_product_index_urls(self, search_url, search_page):
        # get max page item counts
        search_soup = soup(search_page, 'lxml')
        page_footer = search_soup.find('div', {'class': 'footer top-border wrapper'})
        product_count_arr = page_footer.find('span').contents[0].split()
        total_products = int(product_count_arr[-2])
        page_span = int(product_count_arr[0].split('-')[1])
        # get product index pages
        product_index_urls = []
        for page_index in range(1, int(total_products / page_span) + 1):
            product_index_url = search_url + '&cp={}'.format(page_index)
            product_index_urls.append(product_index_url)
        return product_index_urls

    def get_search_url(self, search_str):
        search_url = self.search_base_url + urllib.parse.quote_plus(search_str)
        return search_url

    def get_name(self, product_url, product_page):
        product_soup = soup(product_page, 'lxml')
        name = product_soup.find('div', {'class': 'sku-title', 'itemprop': 'name'}).find('h1').contents[0]
        return name

    def get_dealer(self, product_url, product_page):
        product_soup = soup(product_page, 'lxml')
        dealer = product_soup.find('div', {'class': 'shop-product-title'}).find('a').contents[0]
        return dealer

    def get_price(self, product_url, product_page):
        product_soup = soup(product_page, 'lxml')
        regex = re.compile('price-box pricing-lib-price*')
        price_str = product_soup.find('div', {'class': regex}).find(
            'div', {'class': 'priceView-hero-price priceView-customer-price'}).find(
            'span').contents[0]
        price_str = price_str.replace('$', '').replace(',', '')
        price = float(price_str)
        return price

    def get_inventory(self, product_url, product_page):
        product_soup = soup(product_page, 'lxml')
        buy_button = product_soup.find('div', {'class': 'fulfillment-add-to-cart-button'})
        if buy_button.find(text=re.compile('Add to Cart')) is not None\
            and buy_button.find(text=re.compile('Sold Out')) is None:
            in_stock = True
        else:
            in_stock = False
        return in_stock









