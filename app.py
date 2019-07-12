from flask import Flask, redirect, url_for, render_template, flash, Response, request,jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user,login_required
from oauth import OAuthSignIn
from datetime import date,datetime
from flask_table import Table, Col,LinkCol,NestedTableCol
import json,re
from flask_wtf import FlaskForm
from flask_wtf.csrf import CsrfProtect
from wtforms import StringField,Form,validators
from wtforms.validators import DataRequired, Length,ValidationError

import xlrd
import requests
from lxml import html
import unicodecsv as csv
import amazon_scraper
import snapdeal_scraper

def create_app():
	app = Flask(__name__,static_folder='app/static')
	return app

app= create_app()
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'top secret!'
app.config['WTF_CSRF_ENABLED'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': '1056706187870178',
        'secret': '48039bccdd0d0979e281c103c62fe543'
    }
}
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.init_app(app)
lm.login_view = 'index'

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    dob  =  db.Column(db.String(64), nullable=True)
    gender = db.Column(db.String(64), nullable = True)
    def __repr__(self):
    	return '{} - {}'.format(self.iso, self.nickname)
    def as_dict(self):
    	return {'nickname': self.nickname}

class Userfriends(db.Model):
	__tablename__ = 'Userfriends'
	id = db.Column(db.Integer, primary_key= True)
	f1_id = db.Column(db.String(64), nullable=False)
	f2_id = db.Column(db.String(64), nullable= False)

"""def validate_email(form,field): #Editing Email
	email = form.email.data
	user = User.query.filter_by(email=form.email.data).first()
	if len(email) > 7:
		if re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email) != None:
			return True
		raise ValidationError('This is not a valid email address')

class UserForm(Form):
	email = StringField('email',validators=[DataRequired(), validate_email])"""


#Dataset
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

#BAckend Part

def age(dob):
	today = date.today()
	y = datetime.strptime(dob,'%m/%d/%Y').date()
	age = today.year -y.year - ((today.month, today.day) < (y.month, y.day)) 
	return age

@app.route('/view/<nick>')
def view(nick):
	 results = db.session.query(User).filter_by(nickname=nick).one()
	 a = age(results.dob)
	 if a<4:
		 cat ="Kids"
	 elif a<13:
		cat ="Child"
	 elif a<20:
		cat="Teenager"
	 elif a<32:
		cat = "Young Adult"
	 else:
		if results.gender=="male":
			cat = "Male Adult"
		else:
			cat = "Female Adult"
	 return render_template('category.html',name = results.nickname, email = results.email, g =results.gender, dob=results.dob, masterset = masterset, category = cat)

def names():
	nick = user_friends()
	names=[]
	for x in nick:
		n = db.session.query(User).filter_by(social_id=x).one()
		names.append(n.nickname)
	return names

db.create_all
class Results(Table):
	id = Col('id')
	social_id = Col('social_id')
	nickname = Col('nickname')
	email = Col('email')
	dob = Col('Date of Birth')
	gender = Col('Gender')

class EditTable(Table):
	social_id = Col('social_id')
	nickname = Col('nickname')
	email = Col('email')
	dob = Col('Date of Birth')
	gender = Col('Gender')
	edit = LinkCol('Edit', 'edit')

class Resultfriends(Table):
	id = Col('id')
	f1_id = Col('f1_id')
	f2_id = Col('f2_id')
	#close = Col('close')

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/index',methods=['GET', 'POST'])
def index():
	if request.method =='POST' :
		pr = request.form['proj']
		#return "<h2>"+pr+"</h2>"
		return redirect(url_for('view',nick = pr))
	else:
		return render_template('side_bar.html',upc = upcoming_birthdays(), nick = today(), m=month(), name =names() )

@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/results')# Users Database
def res():
	results =[]
	qry = db.session.query(User)
	results=qry.all()
	table = Results(results)
	table.border = True
	return render_template('results.html', table =table)

@app.route('/friend_list')#friendlist Database
def friend_list():
	results =[]
	qry = db.session.query(Userfriends)
	results=qry.all()
	table = Resultfriends(results)
	table.border = True
	return render_template('results.html', table =table)

"""@app.route('/edit',  methods=['GET', 'POST'])
def edit():
	query = db.session.query(User).filter_by(social_id= current_user.social_id)
	u = query.first()
	if u:
		form = UserForm(formdata=request.form, obj = u)
		if request.method =='POST' and form.validate():
			save_changes(u,form)
			return redirect('/')
		return render_template('edit.html',form = form)
	else:
		return 'Error Loading'"""

@app.route('/view_profile')
@login_required
def view_profile():
	results = []
	x = db.session.query(User).filter_by(social_id=current_user.social_id)
	results = x.one()
	return render_template('profile.html',name = results.nickname, email = results.email, g =results.gender, dob=results.dob)

def save_changes(u, form ):
	u.email = form.email.data
	db.session.commit()

def user_friends():
	nick =[]
	friend = db.session.query(Userfriends).filter_by(f1_id=current_user.social_id).all()
	for x in friend:
		nick.append(x.f2_id)
	return nick

@app.route('/friends')
def friends():
	if current_user.is_anonymous:
		return redirect(url_for('index'))
	else:
		nick =names()
		return render_template('card_list.html',nick = nick)

#@app.route('/upcoming_birthdays')
def upcoming_birthdays():
	if current_user.is_anonymous:
		return redirect(url_for('index'))
	else:
		nick =user_friends()
		u = []
		t = date.today()
		for x in nick:
			dob = []
			n = db.session.query(User).filter_by(social_id=x).one()
			y = n.dob
			y = datetime.strptime(y,'%m/%d/%Y').date()
			y = y.replace(year = t.year)
			dif = y-t
			dif = dif.days
			if (dif<=15 and dif>=1):#do change dif<=15
				dob.append(n.nickname)
				dob.append(n.dob)
				u.append(dob)
		#return render_template('upcoming_birthdays.html',nick = u)
		return u

#@app.route('/this_month')
def month():
	if current_user.is_anonymous:
		return redirect(url_for('index'))
	else:
		nick =user_friends()
		u = []
		t = date.today()
		for x in nick:
			dob = []
			n = db.session.query(User).filter_by(social_id=x).one()
			y = n.dob
			y = datetime.strptime(y,'%m/%d/%Y').date()
			if y.month == t.month:
				dob.append(n.nickname)
				dob.append(n.dob)
				u.append(dob)

		"""	y = y.replace(year = t.year)
			dif = y-t
			dif = dif.days
			if (dif<=15 and dif>=1):#do change dif<=15
				dob.append(n.nickname)
				dob.append(n.dob)
				u.append(dob)"""
		#return render_template('upcoming_birthdays.html',nick = u)
		return u

#@app.route('/today')
def today():
	if current_user.is_anonymous:
		return redirect(url_for('index'))
	else:
		nick =user_friends()
		u = []
		t = date.today()
		for x in nick:
			dob = []
			n =db.session.query(User).filter_by(social_id=x).one()
			y = n.dob
			y = datetime.strptime(y,'%m/%d/%Y').date()
			y = y.replace(year = t.year)
			dif = t-y
			dif = dif.days
			if (dif==0):#do change dif<=15
				dob.append(n.nickname)
				dob.append(y)
				u.append(dob)
		#return render_template('upcoming_birthdays.html',nick = u)
		return u

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email,dob, friend ,g= oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not  user:
        user = User(social_id=social_id, nickname=username, email=email, dob = dob , gender=g)
        db.session.add(user)
        db.session.commit()
    for x in range(len(friend)):
    	res = db.session.query(Userfriends).filter_by(f1_id=social_id,f2_id=friend[x]).all()
    	if not res:
    		f = Userfriends(f1_id= social_id,f2_id= friend[x] )
    		db.session.add(f)
    		db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

@app.route('/product?=<product_category>/gender?=<gender>')
def view_category(product_category,gender):
	if gender=='male':
		gender='Male'
	if gender=='female':
		gender='Female'
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
    db.create_all()
    app.run(debug=True)
