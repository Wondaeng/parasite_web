from flask import Flask, render_template, request, redirect, url_for, flash, session, g
import os, cv2, torchvision, json
from flask_sqlalchemy import SQLAlchemy

from models import db
from models import User
from forms import RegisterForm, UserLoginForm


from flask import session #세션
from flask_wtf.csrf import CSRFProtect #csrf

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


result_path = "./static/results/"
data_path = "./static/user_data/"


def wait_template(query_name):
    return f'''
    <!doctype html>
    <html>
        <head>
            <META HTTP-EQUIV="refresh" CONTENT="30">
        </head>
        <body>
            <h1>Your inference {query_name} is now working</a></h1>

            Please wait a while
            This page keep refresh automatically every 30 seconds.

            <ul>
            <li><a href="/">submit_page</a></li>
            </ul>
        </body>
    </html>

    '''

@app.before_request
def load_logged_in_user():
    
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
        user_result = '/search'
    else:
        g.user = User.query.get(user_id)
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
        if not user:
            user = User(userid=form.userid.data,
                        password=generate_password_hash(form.password.data),
                        email=form.email.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            flash('The user already exists.')
    return render_template('register.html', form=form)


@app.route('/upload', methods=['POST'])
def upload(): # Form is submitted here 

    global data_path
    global result_path

    # Get data from POSTed form
    files = request.files

    if g.user:
        task_name = request.form.get('task_name')
        email = g.user.email
        conf_thres = request.form.get('threshold')
        usr_name = g.user.userid
    else:
        task_name = request.form.get('task_name')
        email = request.form.get('email_adress')
        conf_thres = request.form.get('threshold')
        usr_name = email

    # More setting parameterw will be added HERE
    # Maybe use another DB model for task(s)
    usr_setting = dict()
    usr_setting["user_name"] = usr_name
    usr_setting["task_name"] = task_name
    usr_setting["threshold"] = conf_thres


    # Get path of user data & result
    task_path = os.path.join(data_path, usr_name, task_name)
    task_result_path = os.path.join(result_path, usr_name, task_name)

    # If this is new query, make directories
    if not os.path.exists(task_path):
        os.makedirs(task_path)
        print("!")
    if not os.path.exists(task_result_path):
        os.makedirs(task_result_path)

    with open(os.path.join(task_path, 'setting.json'), 'w') as make_file:
        json.dump(usr_setting, make_file, indent='\t')
    with open(os.path.join(task_path, 'setting.json'), 'w') as make_file:
        json.dump(usr_setting, make_file, indent='\t')

    # Save (image or video) files into the user data folder
    for i in range(len(files)):
        f = files[f'file[{i}]']
        f.save(os.path.join(task_path, f.filename))

    print(f'All filed saved for the task {task_name}')

    return ""


@app.route("/results",methods = ["GET"])
def results_user():
    user_name = g.user.userid
    task_list = [i for i in os.listdir(f'static/results/{user_name}')]
    return render_template('user_results.html', task_list=task_list)


@app.route("/results/<task_name>", methods = ["GET"])
def results_show(task_name):
    
    global data_path
    global result_path
    usr_name = g.user.userid
    # query_id = username
    task_path = os.path.join(data_path, usr_name, task_name)
    task_result_path = os.path.join(result_path, usr_name, task_name)

    # Get images' path from user result directory
    url_lst = [f'results/{usr_name}/{task_name}/{i}' for i in os.listdir(task_path)]

    # Check if the number of image (file) is same between data and result folder
    # Note that video files are converted to frames and removed
    if len(os.listdir(task_path)) == len(os.listdir(task_result_path)):
        return render_template('show_result.html', task_name=task_name, url_lst = url_lst)
    else:
        return wait_template(task_name)


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
