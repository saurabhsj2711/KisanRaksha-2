import datetime

from flask import Flask
from flask_mysqldb import MySQL
import MySQLdb.cursors


# Define a flask app
app = Flask(__name__)
app.secret_key = 'Kisan Raksha'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'sql6.freemysqlhosting.net'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'sql6417892'
app.config['MYSQL_PASSWORD'] = '4twwaugSe8'
app.config['MYSQL_DB'] = 'sql6417892'

mysql = MySQL(app)


def plants_list():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM plants')
    plants = cursor.fetchall()
    list_plant = []
    for plant in plants:
        list_plant.append(plant)

    return list_plant

def posts_list():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM post')
    posts = cursor.fetchall()
    list_post = []
    for post in posts:
        list_post.append(post)

    return list_post

def plantsCount():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    count = cursor.execute('SELECT * FROM plants')
    return count
def diseaseCount():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    count = cursor.execute('SELECT * FROM diseases')
    return count

def usersCount():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    count = cursor.execute('SELECT * FROM user_details')
    return count

def viewsCount():
    counter = 0
    count = 0
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM views')
    views = cursor.fetchall()
    for view in views:
        counter = int(view["views_count"])
        count = count + counter
    return count

def predictionCount():
    counter = 0
    count = 0
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM predictions')
    predictions = cursor.fetchall()
    for prediction in predictions:
        counter = int(prediction["prediction_count"])
        count = count + counter
    return count

def postsCount():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    count = cursor.execute('SELECT * FROM post')
    return count

def queryCount():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    answered_count = cursor.execute('SELECT * FROM user_query WHERE status = %s', ("Answered",))
    not_ans_count = cursor.execute('SELECT * FROM user_query WHERE status = %s', ("Not Answered",))
    return not_ans_count