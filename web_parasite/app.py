from flask import Flask, render_template, request, redirect, url_for
import os, cv2, torchvision


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



@app.route('/')
def index():  # put application's code here
    return render_template('main.html')


@app.route('/upload', methods=['POST'])
def upload():  # put application's code here

    global data_path
    global result_path

    files = request.files
    usr_name = request.form['username']
    usr_path = os.path.join(data_path, usr_name)
    usr_result_path = os.path.join(result_path, usr_name)

    if not os.path.exists(usr_path):
        os.makedirs(usr_path)

    if not os.path.exists(usr_result_path):
        os.makedirs(usr_result_path)

    for i in range(len(files)):
        f = files[f'file[{i}]']
        f.save(os.path.join(usr_path, f.filename))

    print(f'All filed saved for the user {usr_name}')

    return ""


@app.route("/result/<query_id>",methods = ["GET"])
def get_results(query_id):
    
    global data_path
    global result_path

    usr_data_path = os.path.join(data_path, query_id)
    usr_result_path = os.path.join(result_path, query_id) 
    print(len(os.listdir(usr_data_path)),len(os.listdir(usr_result_path)))

    url_lst = [f'results/{query_id}/{i}' for i in os.listdir(usr_data_path)]
    print(url_lst)

    if len(os.listdir(usr_data_path)) == len(os.listdir(usr_result_path)):
        return render_template('result.html', query_id=query_id, url_lst = url_lst)
    else:
        return wait_template(query_id)


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=5002)
