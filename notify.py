from datetime import datetime, timedelta
from flask import Flask
import time
from app import User,Userfriends,create_app
from flask_mail import Mail, Message
from sqlalchemy import extract, and_
import schedule
from datetime import date,datetime

app = create_app()
app.app_context().push()
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'saranya.nukala1@gmail.com',
    "MAIL_PASSWORD": 'avlvsrksnmpjs'
}
app.config.update(mail_settings)
mail = Mail(app)

DAYS_IN_ADVANCE = 0
TODAY = datetime.now() + timedelta(days=DAYS_IN_ADVANCE)

def sent():
  t = date.today()
  users =  User.query.all()
  for x in users:
    friends = Userfriends.query.filter_by(f1_id=x.social_id).all()
    for y in friends:
      ff = User.query.filter_by(social_id= y.f2_id).one()
      d = ff.dob
      d = datetime.strptime(d,'%m/%d/%Y').date()
      d = d.replace(year = t.year)
      d = d-t
      d=d.days
      if d==15:
        msg =Message(subject="GiftuBuddy - Remind to gift your dear.", sender=app.config.get("MAIL_USERNAME"), recipients =[x.email], body="Hey, This is to remind you that your friend"+ff.nickname+" birthday is within 15 days. Follow this link localhost:5000/login to present a gift and be a part to make your friends birthday memorable.")
        m = mail.send(msg)
        print x.nickname +" "+ff.nickname

'''def email():
	msg = Message(subject="Hello",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=['saranya.nukala1@gmail.com'], 
                      body="This is a test email I sent with Gmail and Python!")
	x = mail.send(msg)'''

if __name__ == '__main__':
  #schedule.every(2).minutes.do(email)
  schedule.every().day.at('11:34').do(sent)
  while True:
    schedule.run_pending()
    time.sleep(1)
