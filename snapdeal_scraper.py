import argparse
import requests
import unicodecsv as csv
from lxml import html


def parse(product):
    # url for scraping product details from snapdeal
    url = 'https://www.snapdeal.com/search?keyword={0}'.format(product)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
    failed = False

    # Retries for handling network errors
    for _ in range(5):
        print ("Retrieving %s"%(url))
        response = requests.get(url, headers=headers, verify=False)
        parser = html.fromstring(response.text)
        print ("Parsing page")

        if response.status_code!=200:
            failed = True
            continue
        else:
            failed = False
            break

    if failed:
        return []

    product_listings = parser.xpath('//div[contains(@class,"product-tuple-listing")]')
    scraped_products = []

    print product_listings

    for product in product_listings:
        raw_name = product.xpath('.//p[contains(@class,"product-title")]/text()')        # product name
        raw_price = product.xpath('.//span[contains(@class,"product-price")]//text()')  #price
        raw_url = product.xpath('.//div[contains(@class,"product-tuple-description")]//a/@href')       # product_image
        #raw_rating = product.xpath('//spdp-widget-link noUdLine hashAddedan[@class="a-icon-alt"]//text()')
        raw_image = product.xpath('.//div[contains(@class,"product-tuple-image")]//a//source[contains(@class,"product-image")]/@srcset')

        name  = ' '.join(' '.join(raw_name).split())
        price  = ' '.join(' '.join(raw_price).split())
        price = int(price.replace(" ","").replace(",","").replace("Rs.",""))
        image = ' '.join(' '.join(raw_image).split())
        print type(price)
        data = {
                    'name':name,
                    'price':price,
                    'image':image,
                    'url':raw_url[0],
                    'website':"snapdeal"
        }
        scraped_products.append(data)
    return scraped_products


if __name__=="__main__":

    product = raw_input("product : ")

    scraped_data =  parse(product)
    if scraped_data:
        print ("---- Data is scraped ----")
    else:
        print("No data scraped")
