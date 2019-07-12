from flask import Flask, render_template, url_for, request , redirect
import xlrd
import requests
from lxml import html
import unicodecsv as csv
import amazon_scraper
import snapdeal_scraper

app = Flask(__name__)

workbook = xlrd.open_workbook('Dataset_for_Gifts.xlsx') 	# import values from the dataset
			
masterset = {}												# All the values of data is stored here
sheet_names = ['','Kids','Child','Teenager','Female Adult','Male Adult','Young Adult','Gadgets','Male Clothes','Female Clothes','Sports','Female Accessories','Male Accessories','Male Footwear','Female Footwear','Trail']
category_list = ['Sports','Gadgets','Clothes','Accessories','Footwear']

for index in range(1,workbook.nsheets):						# To find the frequency of each gift
	worksheet = workbook.sheet_by_index(index) 
	dataset = {}
	for row in range(worksheet.nrows):
		for column in range(worksheet.ncols):
			data = worksheet.cell(row,column).value
			if(data!=''):
				if data not in dataset:
					dataset[data] = 1
				dataset[data] += 1
	masterset[sheet_names[index]] = dataset

for index in masterset :									# To find the maximum frequency
	sorted_data = sorted(masterset[index].items(), key=lambda (k,v) : (v,k),reverse=True)
	#sorted_data = dict(sort)
	masterset[index] = sorted_data
	#print index
	#print masterset[index]

@app.route('/home')
def hello_name():
    return render_template('home.html',masterset = masterset, len = len(masterset))


@app.route("/home",methods=["GET","POST"])
def home():
	if request.method == "POST":
		age = request.form["age"]
		gender = request.form["gender"]

	if(age=="kids"):
		category = 'Kids'
	elif(age=='children'):
		category = 'Child'
	elif(age== 'teenager'):
		category = 'Teenager'
	elif(age=='adult'):
		category='Young Adult'
	elif(age=="elderly" and gender=='Female'):
		category = "Female Adult"
	elif(age=='elderly' and gender=='Male'):
		category='Male Adult' 

	return render_template("category.html",gender = gender, category = category,masterset = masterset)


@app.route('/product?=<product_category>/gender?=<gender>')
def view_category(product_category,gender):
	if(product_category in category_list):
		if(product_category in category_list[2::]):
			product_category = gender + " " + product_category
		return render_template("view_product.html",masterset = masterset, product_category = product_category)
	else:
		return redirect(url_for('view_product',product = product_category))


@app.route('/product?=<product>')
def view_product(product):
	
	amazon_scraped_products = amazon_scraper.parse(product)
	snapdeal_scraped_products = snapdeal_scraper.parse(product)
	return render_template("products.html",amazon_scraped_products = amazon_scraped_products,snapdeal_scraped_products = snapdeal_scraped_products)




if __name__ == '__main__':
   app.run(debug = True)



'''
	kids = 0-5
	children = 6-12
	teenager = 13-19
	adult = 20-31
	elderly = 32 +

'''
