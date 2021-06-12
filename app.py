from __future__ import division, print_function
# coding=utf-8
import smtplib, ssl
import os
import re
import numpy as np
import models
# Keras
# from keras.applications.imagenet_utils import preprocess_input, decode_predictions
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template, session, flash, json, jsonify
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from smtplib import SMTPException
import MySQLdb.cursors
from werkzeug.utils import secure_filename

# from gevent.pywsgi import WSGIServer

from datetime import datetime,date


# Define a flask app
app = Flask(__name__)
app.secret_key = 'Kisan Raksha'

# UPLOAD_FOLDER = '../upload'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','h5'}

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'sql6.freemysqlhosting.net'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'sql6417892'
app.config['MYSQL_PASSWORD'] = '4twwaugSe8'
app.config['MYSQL_DB'] = 'sql6417892'

# Intialize MySQL
mysql = MySQL(app)

# Intialize MySQL
# mail = Mail(app)
#
# # Email configurations
app.config['MAIL_DRIVER'] = 'sendmail'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'saurabhsj2711@gmail.com'
app.config['MAIL_PASSWORD'] = 'Saurabh@123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

# Model saved with Keras model.save()
MODEL_PATH = 'model/Cotton.h5'
plant_choosen = False
# Load your trained model
model = load_model(MODEL_PATH)
flag = 0

login_status = False
admin_login_status = False
# grapes_model = load_model(GRAPES_MODEL_PATH)
# Necessary
# print('Model loaded. Start serving...')

# You can also use pretrained model from Keras
# model.save('')
print('Model loaded. Check http://127.0.0.1:5000/')

result = ""


def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(150, 150))

    # Preprocessing the image
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    x = np.expand_dims(x, axis=0)

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
    images = np.vstack([x])
    preds = model.predict_classes(images)
    # preds = model.predict(x)
    return preds


@app.route('/', methods=['GET'])
def index():
    global login_status
    # Main page
    if login_status == False :
         session['loggedin'] = False
         session['id'] = ""
         session['username'] = ""
    list_months = ["January","February","March","April","May","June","July","August","September","October","November","December"]

    current_time = datetime.now()
    print(current_time.month)
    print(current_time.year)
    month = current_time.month
    month = list_months[month-1]
    year = current_time.year
    ####### Add data to views ######################
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM views WHERE views_month = %s and views_year = %s', [month,year])
    views = cursor.fetchone()
    if views :
        print(views)
        count = int(views["views_count"])
        count = count + 1
        cursor.execute('UPDATE views SET views_count = %s WHERE views_month = %s and views_year = %s', [count, month, year])
        mysql.connection.commit()
    else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
        cursor.execute('INSERT INTO views VALUES (NULL, %s, %s, %s)', ["1", month, year])
        mysql.connection.commit()
        msg = 'You have successfully added!'
    list_plants = models.plants_list()
    return render_template('index.html',list_plants = list_plants)


# admin Dashboard api
@app.route('/Admin_dashboard', methods=['GET', 'POST'])
def adminDashboard():

    if admin_login_status == True :
        print(admin_login_status)
        month_list = ["Jan", "Feb", "Mar", "April", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"]
        views_list = [12, 23, 14, 15, 14, 14, 23, 23]
        count_plants = models.plantsCount()
        count_diseases = models.diseaseCount()
        count_users = models.usersCount()
        count_views = models.viewsCount()
        count_prediction = models.predictionCount()
        count_posts = models.postsCount()
        count_not_answered = models.queryCount()
        print(count_plants)
        print(count_diseases)
        print(count_users)
        print(count_views)
        print(count_prediction)
        print(count_posts)
        print(count_not_answered)

        return render_template("Admin_dashboard.html",month_list = month_list,views_list = views_list,count_views=count_views,
                               count_users=count_users,count_plants = count_plants,count_diseases = count_diseases,count_prediction = count_prediction,
                               count_posts = count_posts,count_not_answered=count_not_answered)
    return redirect('/admin_login')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_plant', methods=['POST'])
def add_plant():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file1' not in request.files:
            print('No plant image')
            return redirect(request.url)
        if 'file2' not in request.files:
            print('No h5 file')
            return redirect(request.url)

        plant_image = request.files['file1']
        h5_file = request.files['file2']
        # if user does not select file, browser also
        # submit an empty part without filename
        if plant_image.filename == '' and h5_file.filename == '':
            print('No selected file')
            return redirect(request.url)

        if plant_image and allowed_file(plant_image.filename) and h5_file and allowed_file(h5_file.filename):
            plant = request.form["plant"]
            print(plant)

            session["add_plant"] = plant

            print("uploading")
            basepath_plant_image = os.path.dirname(__file__)
            file_path_image = os.path.join(
            basepath_plant_image+'/static', 'images', secure_filename(plant_image.filename))

            basepath_h5 = os.path.dirname(__file__)
            file_path_h5 = os.path.join(
                basepath_h5, 'model', secure_filename(h5_file.filename))

            plant_image.save(file_path_image)
            h5_file.save(file_path_h5)

            #adding the plant to database
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM plants WHERE plant_name = %s', [plant])
            account = cursor.fetchone()
            # If plant exists show error and validation checks
            if account:
                print('Plant already exists!')
                return render_template("Admin_add_plant.html",count_not_answered = models.queryCount())

            # plant doesnt exists and the form data is valid, now insert new plant into plants table
            cursor.execute('INSERT INTO plants VALUES (NULL, %s)', [plant])
            mysql.connection.commit()
            print('You have successfully added plant!')
            print("uploaded")
            return redirect('/add_disease')
    global admin_login_status
    if admin_login_status == True :
        return render_template("Admin_add_plant.html",count_not_answered = models.queryCount())
    return redirect('/admin_login')

@app.route("/postskill",methods=["POST","GET"])
def postskill():
    if session["add_plant"] == None :
        return redirect('/upload')
    if request.method == 'POST':

        disease_name = request.form.getlist('disease_name[]')
        causes = request.form.getlist('causes[]')
        symptoms = request.form.getlist('symptoms[]')
        management = request.form.getlist('management[]')
        solution = request.form.getlist('solution[]')

        plant = session["add_plant"]
        print(plant)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT plant_id FROM plants WHERE plant_name = %s', (plant,))
        plant_id = cursor.fetchone()
        print(plant_id["plant_id"])
        print(disease_name[0])
        print(causes[0])
        print(symptoms[0])
        print(management[0])
        print(solution[0])

        for i in range(len(disease_name)):
            cursor.execute("INSERT INTO diseases (plant_id,disease_name,cause,symptoms,management,solution) VALUES (%s,%s,%s,%s,%s,%s)",[plant_id["plant_id"],disease_name[i],causes[i],symptoms[i],management[i],solution[i]])
            mysql.connection.commit()


        print(disease_name)
        print(causes)
        print(symptoms)
        print(management)
        print(solution)

        msg = 'New record created successfully'
    return jsonify(msg)

######################### End Planr ###########################

# admin
@app.route('/add_disease', methods=['GET'])
def addDisease():
    global admin_login_status
    if admin_login_status == True :
        return render_template('Admin_add_disease.html',count_not_answered = models.queryCount())
    return redirect('/admin_login')


# admin
@app.route('/add_plant', methods=['GET'])
def addPlant():
    global admin_login_status
    if admin_login_status == True:
        return render_template('Admin_add_plant.html',count_not_answered = models.queryCount())
    return redirect('/admin_login')


# admin
@app.route('/plant_list', methods=['GET'])
def plantList():
    global admin_login_status
    if admin_login_status == True:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM plants')

        # Fetch one record and return result
        results = cursor.fetchall()
        list_plant = []

        l_diseases = []
        for row in results:
            list_plant.append(row)

        print(list_plant)
        return render_template('Admin_plant_list.html', list_plant=list_plant,count_not_answered = models.queryCount())
    return redirect('/admin_login')



# admin
@app.route('/add_post', methods=['GET','POST'])
def addPost():
    if request.method == 'GET':
        global admin_login_status
        if admin_login_status == True:
            return render_template("Admin_add_post.html",count_not_answered = models.queryCount())
        return redirect('/admin_login')


    # Get the file from post request
    f = request.files['file']
    # Save the file to ./uploads
    print("upload")
    basepath = os.path.dirname(__file__)
    file_path = os.path.join(
        basepath, 'static/posts', secure_filename(f.filename))
    f.save(file_path)
    print("Image uploaded")
    # Create variables for easy access
    post_filename = f.filename
    post_author = request.form['author_name']
    post_heading = request.form['heading']
    post_data = request.form['data']

    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Account doesnt exists and the form data is valid, now insert new account into accounts table
    cursor.execute('INSERT INTO post VALUES (NULL, %s, %s, %s,%s,%s)', [post_author,formatted_date, post_heading, post_data,post_filename])
    mysql.connection.commit()

    return render_template("Admin_dashboard.html",count_not_answered = models.queryCount())



# admin
@app.route('/add_users', methods=['GET', 'POST'])
def addUsers():
    if request.method == 'GET':
        global admin_login_status
        if admin_login_status == True:
            return render_template("Admin_add_users.html",list_user = list_users(),count_not_answered = models.queryCount())
        return redirect('/admin_login')


    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form and 'mobile' in request.form:
        # Create variables for easy access
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        mobile = request.form['mobile']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_details WHERE email_id = %s', [email])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
            return render_template("Admin_add_users.html")

        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
            return render_template("Admin_add_users.html")

        elif not re.match(r'[A-Za-z]+', name):
            msg = 'Users Name must contain only characters .!'
            return render_template("Admin_add_users.html")

        elif not re.match(r'^\d{10}$', mobile):
            msg = 'Invalid Mobile Number'
            return render_template("Admin_add_users.html")

        elif not name or not password or not email or not mobile:
            msg = 'Please fill out the form!'
            return render_template("Admin_add_users.html")

        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO user_details VALUES (NULL, %s, %s, %s,%s)', [name, mobile, email, password])
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            flash(msg, "success")
            return render_template('Admin_users_list.html',list_user = list_users(),count_not_answered = models.queryCount())
            # return here where you want to redirect
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        return render_template("Admin_add_users.html",count_not_answered = models.queryCount())

# admin
@app.route('/disease_list/<string:plant_name>', methods=['GET'])
def diseaseList(plant_name):
    if request.method == 'GET':
        global admin_login_status
        if admin_login_status == True:
            print(plant_name)
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT plant_id FROM plants WHERE plant_name = %s", [plant_name])
            id = cur.fetchone()
            print(id)
            result = cur.execute("SELECT * FROM diseases WHERE plant_id = %s", [id['plant_id']])
            disease = cur.fetchall()
            diseaseArray = []
            for row in disease:
                diseaseObj = {
                    'id': row['disease_id'],
                    'name': row['disease_name']}
                diseaseArray.append(diseaseObj)
                print(diseaseObj)
            print(diseaseArray)
            return render_template("Admin_disease_list.html", diseaseArray=diseaseArray,count_not_answered = models.queryCount())
        return redirect('/admin_login')


# admin
@app.route('/admin_login', methods=['GET','POST'])
def adminLogin():
    if request.method == 'GET':

        return render_template("Admin_login.html")
    password = request.form["password"]
    if password == "KISAN@RAKSHA":
        global admin_login_status
        admin_login_status = True
        return  redirect('/Admin_dashboard')
    return render_template("Admin_login.html")

@app.route('/admin_logout', methods=['GET'])
def adminLogout():
    global admin_login_status
    admin_login_status = False
    print(admin_login_status)
    return redirect('/admin_login')

# admin
@app.route('/queries_list', methods=['GET'])
def queriesList():
    if request.method == 'GET':
        global admin_login_status
        if admin_login_status == True:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM user_query WHERE status=%s ', ("Not Answered",))
            # Fetch one record and return result

            results = cursor.fetchall()
            list_queries = []
            for row in results:
                if row["status"] == "Not Answered":
                    list_queries.append(row)
            return render_template("Admin_queries_list.html", list_queries=list_queries,count_not_answered = models.queryCount())
        return redirect('/admin_login')



# admin
@app.route('/replies_list/<string:user_mail>/<string:query>', methods=['GET','POST'])
def repliesList(user_mail,query):
    if request.method == 'GET':
        global admin_login_status
        if admin_login_status == True:
            return render_template("Admin_replies_list.html",user_mail=user_mail,query=query,count_not_answered = models.queryCount())
        return redirect('/admin_login')

    if request.method == "POST":
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "saurabh2711sj@gmail.com"  # Enter your address
        receiver_email = user_mail # Enter receiver address
        password = "Saurabh@one1two2three3"

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_query WHERE user_mail = %s', [user_mail])
        user = cursor.fetchone()
        username = user["username"]
        reply = request.form["solution"]
        message = "Dear "+username+",\n"+reply+"\nThank you."
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE user_query SET status=%s where user_mail=%s', ("Answered",receiver_email))
            mysql.connection.commit()
            msg = 'You have successfully Answered the query!'

            print("Sending...")
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
            print("Sent")
            return redirect("/queries_list")


# admin
@app.route('/solutions', methods=['GET'])
def solutions():
    if request.method == 'GET':
        return render_template("Admin_solutions.html",count_not_answered = models.queryCount())



# admin
@app.route('/admin_post/<string:heading>/<string:author>', methods=['GET'])
def adminShowPost(heading,author):
    if request.method == 'GET':
        global admin_login_status
        if admin_login_status == True:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM post WHERE post_author = %s and post_heading = %s', [author, heading])
            post = cursor.fetchone()
            return render_template("Admin_post.html", post=post,count_not_answered = models.queryCount())
        return redirect('/admin_login')

#admin
@app.route('/admin_delete_post/<string:heading>/<string:author>', methods=['GET'])
def deletePost(heading,author):
    if request.method == 'GET':
        global admin_login_status
        if admin_login_status == True:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("Delete from post WHERE post_author = %s and post_heading = %s", (author,heading))
            mysql.connection.commit()
            return redirect('/admin_post_list')
        return redirect('/admin_login')

#user
@app.route('/post/<string:heading>/<string:author>', methods=['GET'])
def showPost(heading,author):
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM post WHERE post_author = %s and post_heading = %s', [author,heading])
        post = cursor.fetchone()
        return render_template("post.html",post=post,count_not_answered = models.queryCount())

#user
@app.route('/post_select', methods=['GET'])
def selectPost():
    if request.method == 'GET':
        list_post = models.posts_list()
        print(list_post)
        return render_template('select_post.html', list_post=list_post,count_not_answered = models.queryCount())


#user
@app.route('/admin_post_list', methods=['GET'])
def adminListPost():
    if request.method == 'GET':
        global admin_login_status
        if admin_login_status == True:
            list_post = models.posts_list()
            print(list_post)
            return render_template('list_posts.html', list_post=list_post,count_not_answered = models.queryCount())
        return redirect('/admin_login')

#admin
@app.route('/update_solutions', methods=['GET'])
def selectPlant():
    if request.method == 'GET':
        global admin_login_status
        if admin_login_status == True:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM plants ')

            # Fetch one record and return result
            results = cursor.fetchone()
            list_plant=[]
            for plant in results:
                list_plant.append(plant)

            return render_template("Admin_select_plant.html",list_plant=models.plants_list(),count_not_answered = models.queryCount())
        return redirect('/admin_login')



# admin
@app.route('/update_solutions/<string:disease_name>', methods=['GET','POST'])
def updateSolution(disease_name):
    if request.method == 'GET':
        global admin_login_status
        if admin_login_status == True:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM diseases WHERE disease_name=%s',(disease_name,))

            # Fetch one record and return result
            results = cursor.fetchone()

            return render_template("Admin_update_solutions.html",results=results,list_plant=models.plants_list(),count_not_answered = models.queryCount())
        return redirect('/admin_login')

    # POST method to save the updates to database
    new_disease_name = request.form["disease_name"]
    causes = request.form["causes"]
    symptoms = request.form["symptoms"]
    management = request.form["management"]
    solution = request.form["solution"]

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Update the account details
    cursor.execute('UPDATE diseases SET disease_name = %s , cause = %s , symptoms = %s , management = %s , solution = %s WHERE disease_name = %s',
                   (new_disease_name, causes, symptoms, management,solution,disease_name))
    mysql.connection.commit()
    print("Disease updated ... ")
    return render_template("Admin_select_plant.html",list_plant=models.plants_list())


# admin update page function
def update_data(email):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user_details WHERE email_id = %s', (email,))
    # Fetch one record and return result

    results = cursor.fetchone()
    return results


# admin
@app.route('/update_user/<string:email>', methods=['GET', 'POST'])
def updateUsers(email):
    print("updating")
    if request.method == 'GET':
        global admin_login_status
        if admin_login_status == True:
            results = update_data(email)
            return render_template("Admin_update_user.html", results=results,count_not_answered = models.queryCount())
        return redirect('/admin_login')

    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'mobile' in request.form:
        # Create variables for easy access
        print("post")
        name = request.form['name']

        new_email = request.form['email']
        mobile = request.form['mobile']
        # Check if account exists using MySQL
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM user_details WHERE email_id = %s', [email])

        # account = cursor.fetchone()
        # If account exists show error and validation checks

        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
            results = update_data(email)
            return render_template("Admin_update_user.html", results=results,count_not_answered = models.queryCount())

            # return redirect(request.url)

        elif not re.match(r'[A-Za-z]+', name):
            msg = 'Users Name must contain only characters .!'
            results = update_data(email)
            return render_template("Admin_update_user.html", results=results,count_not_answered = models.queryCount())

            # return redirect(request.url)

        elif not re.match(r'^\d{10}$', mobile):
            msg = 'Invalid Mobile Number'
            results = update_data(email)
            return render_template("Admin_update_user.html", results=results,count_not_answered = models.queryCount())

            # return redirect(request.url)

        elif not name or not email or not mobile:
            results = update_data(email)
            msg = 'Please fill out the form!'

            # return redirect(request.url)

        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            # Update the account details
            cursor.execute('UPDATE user_details SET name = %s , email_id = %s , mobile_no = %s WHERE email_id = %s',
                           (name, new_email, mobile, email))
            print(name,mobile,email,new_email)
            mysql.connection.commit()
            print('You have successfully updated!')
            # flash(msg,"success")
            print('hello123')
            return render_template('Admin_users_list.html', list_user=list_users(),count_not_answered = models.queryCount())
            # return here where you want to redirect
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'

        results = update_data(email)
        return render_template("Admin_update_user.html", results=results,count_not_answered = models.queryCount())


# admin table delete user api
@app.route("/delete_user/<string:email>", methods=["GET", "POST"])
def delete_user(email):
    if request.method == "GET":
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("Delete from user_details WHERE email_id = %s", (email,))
        mysql.connection.commit()

        return render_template('Admin_users_list.html', list_user=list_users(),count_not_answered = models.queryCount())
    return render_template("Admin_update_user.html", results=update_data(email),count_not_answered = models.queryCount())





# admin
def list_users():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    print("cursor created")
    cursor.execute('SELECT * FROM user_details')
    print("data selected")
    # Fetch one record and return result

    results = cursor.fetchall()
    list_user = []
    for row in results:
        list_user.append(row)
    return list_user


@app.route('/users_list', methods=['GET'])
def userList():
    global admin_login_status
    if admin_login_status == True:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        print("cursor created")
        cursor.execute('SELECT * FROM user_details')
        print("data selected")
        # Fetch one record and return result

        results = cursor.fetchall()
        list_user = []
        for row in results:
            list_user.append(row)

        return render_template("Admin_users_list.html", list_user=list_user,count_not_answered = models.queryCount())
    return redirect('/admin_login')



# FrontEnd

@app.route('/crops', methods=['GET'])
def crops():
    global login_status
    if login_status == False:
        return render_template('log_in.html')
    list_plants = models.plants_list()
    return render_template('crops.html',list_plants = list_plants)


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "saurabh2711sj@gmail.com"  # Enter your address
        receiver_email = request.form["email"]  # Enter receiver address
        password = "Saurabh@one1two2three3"
        f_name = request.form["first_name"]
        l_name = request.form["last_name"]
        username = f_name+" "+l_name
        query = request.form["comments"]
        message = "Dear "+username+"\nWe have registered your query.Thank you for contacting us for your query. We are glad to solve your query as soon as possible .\nWe will reach out to you soon through the mail within 3 days.\nThank you."
        print(username)
        print(receiver_email)
        print(message)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO user_query VALUES (NULL, %s, %s, %s, %s)', [username,receiver_email, query ,"Not Answered"])
            mysql.connection.commit()
            msg = 'You have successfully registered query!'

            print("Sending...")
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
            print("Sent")
            flash("Thank you for contacting . Your query will be reviewed soon ", "success")
            return render_template('contact.html')
    return render_template('contact.html')

###########################End of appy.py################

@app.route('/upload_image/<string:plant>', methods=['GET'])
def image_upload(plant):
    global plant_choosen
    plant_choosen = True
    session["plant_choosen"] = plant

    global flag, model, MODEL_PATH
    flag = 0

    MODEL_PATH = 'model/' + session["plant_choosen"] + '.h5'

    model = load_model(MODEL_PATH)
    if session["username"] == "":
        flash("Please login !", "warning")
        return redirect("/log_in")
    return render_template('upload_image.html',plant = plant)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form and 'mobile' in request.form:
        # Create variables for easy access
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        mobile = request.form['mobile']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_details WHERE email_id = %s', [email])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
            # return redirect(request.url)

        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
            # return redirect(request.url)

        elif not re.match(r'[A-Za-z]+', name):
            msg = 'Users Name must contain only characters .!'
            # return redirect(request.url)

        elif not re.match(r'^\d{10}$', mobile):
            msg = 'Invalid Mobile Number'
            # return redirect(request.url)

        elif not name or not password or not email or not mobile:
            msg = 'Please fill out the form!'
            # return redirect(request.url)

        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO user_details VALUES (NULL, %s, %s, %s,%s)', [name, mobile, email, password])
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            print("Registered..")
            flash(msg, "success")
            return redirect('/log_in')
            # return here where you want to redirect
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'

    # Show registration form with message (if any)
    return render_template('register.html')


@app.route('/log_in', methods=['GET', 'POST'])
def log_in():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_details WHERE email_id = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            global login_status
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['uid']
            session['username'] = account['name']
            flash("Logged in Successfully", "success")
            login_status = True
            if plant_choosen == False :
                return redirect("/crops")
            return render_template('upload_image.html',plant = session["plant_choosen"])

            # Redirect to home page after login
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            return render_template('log_in.html',msg = msg)

    return render_template('log_in.html')


@app.route('/logout')
def logout():
    global login_status,plant_choosen
    login_status = False
    plant_choosen = False
    # remove the username from the session if it is there
    session.pop('username', None)
    session.pop('id', None)
    session['loggedin'] = False
    # flash('Looks like '+old_user+' have logged out!')
    return redirect('/')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    global result, flag, MODEL_PATH
    print("flag : ", flag)
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']
        # Save the file to ./uploads
        print("upload")
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'upload', secure_filename(f.filename))
        f.save(file_path)
        print("Image uploaded")

        # Make prediction
        list_diseases =[]
        if session["plant_choosen"] == "Cotton" :
            list_diseases = ["Not identified"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT plant_id FROM plants WHERE plant_name = %s', (session["plant_choosen"],))
        # Fetch one record and return result
        id = cursor.fetchone()
        print(id)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT disease_name FROM diseases WHERE plant_id = %s', (id["plant_id"],))
        # Fetch one record and return result
        diseases = cursor.fetchall()

        for disease in diseases :
            print(disease)
            list_diseases.append(disease["disease_name"])

        preds = model_predict(file_path, model)
        print(preds[0])
        print(list_diseases)


        result = "" + list_diseases[preds[0]]
        print(result)
        return result


    print("None")
    return None


@app.route('/disease-info', methods=['GET'])
def info():

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute('SELECT * FROM prediction WHERE disease_name = %s', (result,))

    # Fetch one record and return result
    disease_data = cursor.fetchone()

    ############### Add prediction count #################
    list_months = ["January","February","March","April","May","June","July","August","September","October","November","December"]

    current_time = datetime.now()
    print(current_time.month)
    print(current_time.year)
    month = current_time.month
    print(month)
    month = list_months[month - 1]
    print(month)
    year = current_time.year
    ####### Add data to views ######################
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM predictions WHERE prediction_month = %s and prediction_year = %s', [month, year])
    predictions = cursor.fetchone()
    if predictions:
        print(predictions)
        count = int(predictions["prediction_count"])
        count = count + 1
        cursor.execute('UPDATE predictions SET prediction_count = %s WHERE prediction_month = %s and prediction_year = %s',
                       [count, month, year])
        mysql.connection.commit()
    else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
        cursor.execute('INSERT INTO predictions VALUES (NULL, %s, %s, %s)', ["1", month, year])
        mysql.connection.commit()
        msg = 'You have successfully added!'

    ######################################################
    # Process your result for human
    print(disease_data["disease_name"], disease_data["cause"], disease_data["symptoms"], disease_data["management"],
          disease_data["solution"])
    return render_template("text.html", disease_data=disease_data)


if __name__ == '__main__':
    app.run(debug=True)
