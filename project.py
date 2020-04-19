
from flask import Flask, render_template, redirect, url_for, request, session
from bcrypt import hashpw, gensalt
import sqlalchemy as db
from flask import g
from datetime import datetime
from time import time
import json

import urllib.request
import requests
engine = db.create_engine('mysql://root:12345678@project.cvemnhulbj6l.us-east-1.rds.amazonaws.com:3306/forum', echo=True)
connection = engine.connect()
metadata = db.MetaData()
app = Flask(__name__)

app.secret_key = "1231231231233"
from flask_wtf  import Form
from wtforms import TextField, PasswordField,TextAreaField
from wtforms.validators import  Required, EqualTo, \
    Length, ValidationError
import mysql.connector
from mysql.connector import Error

mydb = mysql.connector.connect(
  host="project.cvemnhulbj6l.us-east-1.rds.amazonaws.com",
  port="3306",
  user="root",
  passwd="12345678",
  database="forum"
)



class ReplyForm(Form):
    content = TextAreaField("Reply", validators=[Required()])

class NewTopicForm(Form):
    subject = TextField("Subject", validators=[Required()])
    content = TextAreaField("Claim", validators=[Required()])

def query_db(query, args=(), one=False):
    mycursor = mydb.cursor()
    mycursor.execute(query)

    myresult = mycursor.fetchall()

    rv = [dict((mycursor.description[idx][0], value)
               for idx, value in enumerate(row)) for row in myresult]
    return (rv[0] if rv else None) if one else rv

def format_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d @ %I:%M %p')

def format_elapsed_datetime(times):
    seconds = int(time()) - int(times)
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    if days > 1:
        return "%i days ago" % days
    elif days == 1:
        return "1 day ago"
    elif hours > 1:
        return "%i hours ago" % hours
    elif hours == 1:
        return "1 hour ago"
    elif minutes > 1:
        return "%i minutes ago" % minutes
    elif minutes == 1:
        return "1 minute ago"
    elif seconds > 1:
        return "%i seconds ago" % seconds
    else:
        return "1 second ago"
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return  redirect("/topics")
# Route for handling the login page logic
@app.before_request
def before_request():
    # look up the current user
    g.username = None
    if "username" in session:
        g.username = query_db("SELECT * FROM login where username = '"+session["username"]+"'", one=True)["username"]        
    
@app.route('/topics')
def topics():
    # get a list of topics sorted by the date of their last reply
    topics = query_db("SELECT * FROM topic ORDER BY (SELECT MAX(time) FROM \
            claim WHERE claim.topic_id = topic.topic_id) DESC")
    print(topics)
    for topic in topics:
        # get number of replies to topic
        reply_count = query_db("SELECT count(*) FROM claim WHERE topic_id = "+ 
                str(topic["topic_id"]), one=True)["count(*)"]
        topic["replies"] = reply_count - 1
        # get date of most recent reply
        last_reply = query_db("SELECT time FROM claim WHERE topic_id ="+  str(topic["topic_id"])+" ORDER \
                BY time DESC LIMIT 1", one=True)["time"]
        topic["last_reply_date"] = last_reply
    api = 'c3e2e2cfca1d4f75f45c4044f2273343'
    url='http://api.openweathermap.org/data/2.5/weather?q=london&appid=' + api
    source = requests.get(url)
    list_of_data = json.loads(source.content.decode())
    print(str(list_of_data['main']['temp']) + 'k')
        
    return render_template("topics.html", topics=topics,temp=str(list_of_data['main']['temp']) + 'k')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop("username", None)
    g.username = None
    return redirect("/login")
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        login = db.Table('login', metadata, autoload=True, autoload_with=engine)
        query=db.select([login]).where(login.columns.username == request.form['username'] )
        queryexec = connection.execute(query)
        is_login = queryexec.fetchall()        
        #Take the hashkey and password from form and encrypt again
        pw_hash = hashpw(request.form['password'].encode('utf-8'),is_login[0][3].encode('utf-8') )
        #If encrypted and that in Db match load page
        if pw_hash!=is_login[0][2].encode('utf-8'):
            error = 'Invalid Credentials. Please try again.'
        else:
            session["username"] = is_login[0][1] 
            session['logged_in'] = True

            session['is_login']='success'
            return  redirect("/topics")
    return render_template('login.html', error=error)

app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['datetimeelapsedformat'] = format_elapsed_datetime

@app.route('/topic/new', methods=['GET', 'POST'])
def new_topic():
    form = NewTopicForm()
    if form.validate_on_submit():
        print(form.subject.data)
        new_topic_id = post_topic(form.subject.data, form.content.data)
        return redirect('/topic/' + new_topic_id)
    return render_template("newtopic.html", form=form)
@app.route('/topic/<topic_id>', methods=['GET', 'POST'])
def view_topic(topic_id):
    # view or post to a topic
    subject = query_db("SELECT subject FROM topic WHERE topic_id = "+ 
            topic_id, one=True)
    if subject is None:
        abort(404)
    subject = subject["subject"]
    
    form = ReplyForm()
    if form.validate_on_submit():
        # need to be logged in
        if not g.username:
            abort(403)
        post_reply(topic_id, form.content.data)
    
    replies = query_db("SELECT * FROM claim WHERE topic_id = "+topic_id+" ORDER BY time")
    return render_template("topic.html", subject=subject, replies=replies, 
                           form=form)
    
def post_topic(subject, content):
    mycursor = mydb.cursor()

    query="INSERT INTO topic (subject) values ('"+subject+ "')"
    mycursor.execute(query)
    topic_id = query_db("select LAST_INSERT_ID() ")[0]["LAST_INSERT_ID()"]
    topic_id = str(topic_id)
    post_reply(topic_id, content)
    return topic_id
def post_reply(topic_id, content):
    
    mycursor = mydb.cursor()
    query="INSERT INTO claim (topic_id, time, content, author) values ('"+topic_id+"','"+str(int(time()))+"','"+content+"','"+g.username+ "')"
    mycursor.execute(query)

if __name__=="__main__":

    app.run(debug=False,threaded=True,host='0.0.0.0')
