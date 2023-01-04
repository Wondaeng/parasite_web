from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import os, cv2, torchvision, json
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

from models import db
from models import User, Task
from forms import RegisterForm, UserLoginForm, FileUploadForm


from flask import session #세션
from flask_wtf.csrf import CSRFProtect #csrf

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import pandas as pd
import mimetypes

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'trypa.screening@gmail.com'
app.config['MAIL_PASSWORD'] ='kyfwwjrnyypkhysw'
app.config['MAIL_DEFAULT_SENDER'] = 'trypa.screening@gmail.com'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_MAX_EMAILS'] = False
app.config['MAIL_ASCII_ATTACHMENTS'] = False
mail = Mail(app)


result_path = "./static/results/"
data_path = "./static/user_data/"

"""def send_email(user_name, user_email, task_name, info_type):
    if not user_name:  # If guest user
        if info_type == 'finish':
            msg = Message(f'Your job is finished! - {task_name}', sender=('Trypa Screening', 'trypa.screening@gmail.com'), recipients=[f'{user_email}'])
            msg.body = '''Your job is finished! Go to search page and check it out. (http://223.194.227.150:5002/)'''
        elif info_type == 'submit':
            msg = Message(f'Your job is submitted! - {task_name}', sender=('Trypa Screening', 'trypa.screening@gmail.com'), recipients=[f'{user_email}'])
            msg.body = '''Your job is submitted! We will notify you through email when the job is finihsed. (http://223.194.227.150:5002/)'''
    else:  # If user logged in
        if info_type == 'finish':
            msg = Message(f'Your job is finished! - {task_name}', sender=('Trypa Screening', 'trypa.screening@gmail.com'), recipients=[f'{user_email}'])
            msg.body = '''Your job is finished! Login and go to result page. (http://223.194.227.150:5002/)'''
        elif info_type == 'submit':
            msg = Message(f'Your job is submitted! - {task_name}', sender=('Trypa Screening', 'trypa.screening@gmail.com'), recipients=[f'{user_email}'])
            msg.body = '''Your job is submitted! We will notify you through email when the job is finihsed. (http://223.194.227.150:5002/)'''
    mail.send(msg)
    return 'email is sent'"""



@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
        user_result = '/search'
    else:
        g.user = User.query.get(user_id)
        print(g.user.userid)
        user_result = '/results/' + g.user.userid

@app.route('/')
def index():  # Render main page html
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
        user_result = '/search'
    else:
        g.user = User.query.get(user_id)
        user_name = g.user.userid
        user_result = '/results/' + user_name
    
    return render_template('main.html', result_path=user_result)


@app.route('/search', methods=['GET','POST'])
def search():  # Task search page for a guest user
    if request.method == 'GET':
        return render_template('search.html')
    else:
        email = request.form['email']
        task_name = request.form['task_name']
        return redirect(url_for('videos_guest', email=email, task_name=task_name))
@app.route('/help', methods=['GET'])
def help():  # Help page
    return render_template('help.html')


@app.route('/login', methods=['GET','POST'])
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(userid=form.userid.data).first()
        if not user:
            error = "User ID does not exist."
        elif not check_password_hash(user.password, form.password.data):
            error = "The password is incorrect."
        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))
        flash(error)
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(userid=form.userid.data).first()
        email = User.query.filter_by(email=form.email.data).first()
        print(email)
        if (not user) and (not email):
            user = User(userid=form.userid.data,
                        password=generate_password_hash(form.password.data),
                        email=form.email.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))
        elif user and (not email):
            flash('The user name already exists.')
        elif (not user) and email:
            flash('The email adress is already used.')
        else:
            flash('The user name already exists.')
    return render_template('register.html', form=form)


@app.route('/upload', methods=['POST'])
def upload(): # Form is submitted here 

    global data_path
    global result_path

    form = FileUploadForm()

    # Get data from POSTed form
    files = request.files
    task_name = form.task_name.data
    
    if g.user:
        usr_name = form.user_name.data
        task = Task.query.filter_by(task_name=form.task_name.data).filter_by(user_name=form.user_name.data).first()
        print(1, usr_name)
    else:
        usr_name = form.email_adress.data.replace('@', '%40')
        task = Task.query.filter_by(task_name=form.task_name.data).filter_by(user_name=usr_name).first()
        print(2, usr_name, task)

    if not task:
        task_name = form.task_name.data
        date_time  = datetime.now()
        date_time_str = date_time.strftime("%Y-%m-%d %H:%M:%S")
        sens_thres = form.sensitivity.data
        visual_path = os.path.join(result_path, usr_name, task_name)

        print(usr_name)

        task = Task(task_name=task_name, user_name=usr_name, date=date_time_str, visual_path=visual_path, sensitivity=sens_thres, process_stage='queued')

        db.session.add(task)
        db.session.commit()

        # Get path of user data & result
        task_path = os.path.join(data_path, usr_name, task_name)
        task_result_path = os.path.join(result_path, usr_name, task_name)

        # If this is new query, make directories
        if not os.path.exists(task_path):
            os.makedirs(task_path)

        if not os.path.exists(task_result_path):
            os.makedirs(task_result_path)

        # Save (image or video) files into the user data folder
        for i in range(len(files)):
            f = files[f'file[{i}]']
            file_name = f.filename
            file_path = os.path.join(task_path, file_name).replace(' ', '\ ')
            if mimetypes.guess_type(file_path)[0].startswith('video'):  # If the file is video 
                os.makedirs(os.path.join(task_path, os.path.splitext(file_name)[0]))
                os.makedirs(os.path.join(task_result_path, os.path.splitext(file_name)[0]))
                f.save(os.path.join(task_path, os.path.splitext(file_name)[0], file_name))
            else:  # If the file is image
                # If there is at least one image, make new directory to group images
                f.save(os.path.join(task_path, file_name))

                
                image_dir = os.path.join(task_path, 'images')
                image_result_dir = os.path.join(task_result_path, 'images')

                if not os.path.exists(image_dir):
                    os.makedirs(image_dir)
                if not os.path.exists(image_result_dir):
                    os.makedirs(os.path.join(task_result_path, 'images'))

                # Moves images into the image folder created
                os.system(f'mv {file_path} {image_dir}/{file_name}')
                print(f"Moving image {file_name} into a folder ...")

        print(f'All filed saved for the task {task_name}')

    else:
        flash('The query with the same task name already exists.')
        print('The query with the same task name already exists.')
    
    return ""


@app.route("/results",methods = ["GET"])
def tasks_user():
    try:
        user_name = g.user.userid
        task_list = [i for i in os.listdir(f'static/results/{user_name}')]

        con = sqlite3.connect("db.sqlite")
        task_df = pd.read_sql_query("SELECT * from task_table", con)
        user_task_df = task_df[task_df.user_name == user_name]

        task_stage_list = [user_task_df.loc[task_df.task_name == i,'process_stage'].tolist()[0] for i in task_list]
        date_list = [user_task_df.loc[task_df.task_name == i,'date'].tolist()[0] for i in task_list]
        sensitivity_list = [user_task_df.loc[user_task_df.task_name == i,'sensitivity'].tolist()[0] for i in task_list]
        con.close() 


        task_information = zip(task_list, date_list, sensitivity_list, task_stage_list)
        
        return render_template('user_tasks.html', task_information=task_information, author = user_name)
    except:
        return render_template('user_no_task.html')


@app.route("/results/<task_name>", methods = ["GET"])
def videos_user(task_name):
    
    global data_path
    global result_path
    user_name = g.user.userid
    
    # query_id = username
    task_path = os.path.join(data_path, user_name, task_name)
    task_result_path = os.path.join(result_path, user_name, task_name)
    
    con = sqlite3.connect("db.sqlite")
    task_df = pd.read_sql_query("SELECT * from task_table", con)
    user_task_df = task_df[task_df.user_name == user_name]
    task_stage = user_task_df.loc[user_task_df.task_name == task_name, 'process_stage'].tolist()[0]

    con.close()

    # Get video directories from user result directory
    video_name_lst = [i for i in os.listdir(task_path)]
    video_path_lst = [f'results/{user_name}/{task_name}/{i}' for i in os.listdir(task_path)]
    video_info_lst = zip(video_name_lst, video_path_lst)

    # Note that video files are converted to frames and removed
    # Check if the task is done or not
    if task_stage == 'done':
        print(video_name_lst)
        print(video_path_lst)
        return render_template('task_videos.html', task_name=task_name, video_info_lst = video_info_lst)
        
    else:
        return render_template('wait_template.html', query_name=task_name)

@app.route("/results/<task_name>/<video_name>", methods = ["GET"])
def results_show(task_name, video_name):
    
    global data_path
    global result_path
    if g.user:
        user_name = g.user.userid
    else:
        return
    # query_id = username
    video_path = os.path.join(data_path, user_name, task_name, video_name)
    video_result_path = os.path.join(result_path, user_name, task_name, video_name)
    
    con = sqlite3.connect("db.sqlite")
    task_df = pd.read_sql_query("SELECT * from task_table", con)
    user_task_df = task_df[task_df.user_name == user_name]
    task_stage = user_task_df.loc[user_task_df.task_name == task_name, 'process_stage'].tolist()[0]

    con.close()

    # Get images' path from user result directory
    url_lst = [f'results/{user_name}/{task_name}/{video_name}/{i}' for i in os.listdir(video_result_path)]
    url_lst = [i for i in url_lst if i.endswith('.jpg')]

    metadata_df = pd.read_csv(f'{video_result_path}/metadata.csv')
    bbox_sorted_df = metadata_df.sort_values(by=["bbox_num"], ascending=False)
    bbox_sorted_names = list(bbox_sorted_df["name"])

    conf_sorted_df = metadata_df.sort_values(by=["confidence"], ascending=False)
    conf_sorted_names = list(conf_sorted_df["name"])

    url_lst_bbox = [f'results/{user_name}/{task_name}/{video_name}/{i}' for i in bbox_sorted_names]
    url_lst_conf = [f'results/{user_name}/{task_name}/{video_name}/{i}' for i in conf_sorted_names]


    # Check if the number of image (file) is same between data and result folder
    # Note that video files are converted to frames and removed
    if task_stage == 'done':
        return render_template('show_result.html', video_name=video_name, url_lst = url_lst, url_lst_bbox = url_lst_bbox, url_lst_conf = url_lst_conf)
    else:
        return render_template('wait_template.html', query_name=task_name)

@app.route("/results_guest/<email>/<task_name>", methods = ["GET"])
def videos_guest(email, task_name):
    
    global data_path
    global result_path
    user_name = email.replace('@', '%40')

    # query_id = username
    task_path = os.path.join(data_path, user_name, task_name)
    task_result_path = os.path.join(result_path, user_name, task_name)
    
    try:    
        con = sqlite3.connect("db.sqlite")
        task_df = pd.read_sql_query("SELECT * from task_table", con)
        user_task_df = task_df[task_df.user_name == user_name]
        task_stage = user_task_df.loc[user_task_df.task_name == task_name, 'process_stage'].tolist()[0]
        con.close()
    except:
        return render_template('error.html')

    # Get video directories from user result directory
    video_name_lst = [i for i in os.listdir(task_path)]
    video_path_lst = [f'results/{user_name}/{task_name}/{i}' for i in os.listdir(task_path)]
    video_info_lst = zip(video_name_lst, video_path_lst)

    # Note that video files are converted to frames and removed
    # Check if the task is done or not
    if task_stage == 'done':
        print(video_name_lst)
        print(video_path_lst)
        return render_template('task_videos_guest.html', email = email.replace('%40', '@'), task_name=task_name, video_info_lst = video_info_lst)
        
    else:
        return render_template('wait_template.html', query_name=task_name)


@app.route("/results_guest/<email>/<task_name>/<video_name>", methods = ["GET"])
def results_guest_show(email, task_name, video_name):
    
    global data_path
    global result_path

    user_name = email.replace('@', '%40')

    # query_id = username
    video_path = os.path.join(data_path, user_name, task_name, video_name)
    video_result_path = os.path.join(result_path, user_name, task_name, video_name)
    
    con = sqlite3.connect("db.sqlite")
    task_df = pd.read_sql_query("SELECT * from task_table", con)
    user_task_df = task_df[task_df.user_name == user_name]
    task_stage = user_task_df.loc[user_task_df.task_name == task_name, 'process_stage'].tolist()[0]

    con.close()

    # Get images' path from user result directory
    url_lst = [f'results/{user_name}/{task_name}/{video_name}/{i}' for i in os.listdir(video_result_path)]
    url_lst = [i for i in url_lst if i.endswith('.jpg')]

    metadata_df = pd.read_csv(f'{video_result_path}/metadata.csv')
    bbox_sorted_df = metadata_df.sort_values(by=["bbox_num"], ascending=False)
    bbox_sorted_names = list(bbox_sorted_df["name"])

    conf_sorted_df = metadata_df.sort_values(by=["confidence"], ascending=False)
    conf_sorted_names = list(conf_sorted_df["name"])

    url_lst_bbox = [f'results/{user_name}/{task_name}/{video_name}/{i}' for i in bbox_sorted_names]
    url_lst_conf = [f'results/{user_name}/{task_name}/{video_name}/{i}' for i in conf_sorted_names]

    # Check if the number of image (file) is same between data and result folder
    # Note that video files are converted to frames and removed
    if task_stage == 'done':
        return render_template('show_result.html', video_name=video_name, url_lst = url_lst, url_lst_bbox = url_lst_bbox, url_lst_conf = url_lst_conf)
    else:
        return render_template('wait_template.html', query_name=task_name)


if __name__ == '__main__':
    basedir = os.path.abspath(os.path.dirname(__file__))
    dbfile = os.path.join(basedir, 'db.sqlite')

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile   
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
    app.config['SECRET_KEY'] = 'wcsfeufhwiquehfdx'
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False

    csrf = CSRFProtect()
    csrf.init_app(app)

    app.app_context().push()
    
    db.init_app(app)
    db.app = app
    
    db.create_all()  #db 생성

    app.run(host = '0.0.0.0', port=5002)
