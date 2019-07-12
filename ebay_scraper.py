import argparse
#from pprint import pprint
#from traceback import format_exc

import requests
import unicodecsv as csv
from lxml import html


def parse(brand):

    url = 'https://www.ebay.com/sch/i.html?_nkw={0}&_sacat=0'.format(brand)
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

    product_listings = parser.xpath('//li[contains(@id,"results-listing")]')
    raw_result_count = parser.xpath("//h1[contains(@class,'count-heading')]//text()")
    result_count = ''.join(raw_result_count).strip()    # strips : remove spaces in either sides
    print ("Found {0} for {1}".format(result_count,brand))
    scraped_products = []


    for product in product_listings:
        raw_url = product.xpath('.//a[contains(@class,"item__link")]/@href')        # url 
        raw_title = product.xpath('.//h3[contains(@class,"item__title")]//text()')  # product_name
        raw_product_type = product.xpath('.//h3[contains(@class,"item__title")]/span[@class="LIGHT_HIGHLIGHT"]/text()')
        raw_price = product.xpath('.//span[contains(@class,"s-item__price")]//text()')  #price
        raw_image = product.xpath('.//img[contains(@class,"s-item__image-img")]/@src')       # product_image
        #raw_rating = product.xpath('//div[contains(@class,"b-starrating")]/span[@class,"clipped"]/text()')
        price  = ' '.join(' '.join(raw_price).split())
        title = ' '.join(' '.join(raw_title).split())
        product_type = ''.join(raw_product_type)
        title = title.replace(product_type, '').strip()
        image = ' '.join(' '.join(raw_image).split())
        #rating = ' '.join(' '.join(raw_rating).split())
        data = {
                    'url':raw_url[0],
                    'title':title,
                    'price':price,
                    'image':image,
                    #'rating':rating
        }
        scraped_products.append(data)
    return scraped_products


if __name__=="__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument('brand',help = 'Brand Name')
    args = argparser.parse_args()
    brand = args.brand

    scraped_data =  parse(brand)
    if scraped_data:
        print ("Writing scraped data to %s-ebay-scraped-data.csv"%(brand))
        with open('%s-ebay-scraped-data.csv'%(brand),'wb') as csvfile:
            fieldnames = ["title","price","url","image"]
            writer = csv.DictWriter(csvfile,fieldnames = fieldnames,quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for data in scraped_data:
                writer.writerow(data)
    else:
        print("No data scraped")




#https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw=apple&_sacat=0&LH_TitleDesc=0&_osacat=0&_odkw=mobile+phones&LH_TitleDesc=0

#https://www.ebay.com/sch/i.html?_from=R40&_nkw=apple&_sacat=0&LH_TitleDesc=0&LH_TitleDesc=0&_pgn=2

# amazon

#s-search-results >> span class="rush-component s-latency-cf-section"

#product << div class = "some code for each product " << div class="s-result-list s-search-results sg-row"



'''


    ---- Path of main products ----
<div class = "srp-main srp-main--isLarge"
<div id = "mainContent"
    <div class = srp-river srp-layout-inner"
        <div id = "srp-river-main"
            <div id = "srp-river-results"
                <ul class = "srp-results srp-lists clearfix">
                    <div id ="srp-river-results-listing(123456..)">



'''
