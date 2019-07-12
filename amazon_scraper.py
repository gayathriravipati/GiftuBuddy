import requests
import unicodecsv as csv
from lxml import html

def parse(product):
    # url for scraping details of product from amazon
    url = 'https://www.amazon.in/s?k={0}&ref=nb_sb_noss'.format(product)       
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

    product_listings = parser.xpath('//div[contains(@class,"s-result-item")]')
    scraped_products = []


    for product in product_listings:
        raw_name = product.xpath('.//span[contains(@class,"a-text-normal")]//text()')        # product name
        raw_url = product.xpath('.//a[contains(@class,"a-text-normal")]/@href')              # product url
        raw_price = product.xpath('.//span[@class="a-price"]//text()')                       # product_price
        raw_image = product.xpath('.//img[contains(@class,"s-image")]/@src')                 # product_image
        #raw_rating = product.xpath('//span[@class="a-icon-alt"]//text()')
        name  = ' '.join(' '.join(raw_name).split())
        image = ' '.join(' '.join(raw_image).split())
        if(raw_price):
            data = {
                       'name': name,
                        'price':raw_price[0][1::],
                        'image':image,
                        'url' : "https://www.amazon.in" + raw_url[0],
                        'website':"amazon"
            }
        scraped_products.append(data)
    return scraped_products


if __name__=="__main__":

    product = raw_input("Porduct : ")

    scraped_data =  parse(product)
    if scraped_data:
        print ("---- Data is scraped ----")
    else:
        print("No data scraped")

