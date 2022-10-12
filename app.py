from flask import Flask, render_template, request, redirect, url_for
import os, cv2, torchvision, json


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
def index():  # Render main page html
    return render_template('main.html')


@app.route('/upload', methods=['POST'])
def upload(): # Form is submitted here 
    global data_path
    global result_path

    # Get data from POSTed form
    files = request.files

    usr_name = request.form.get('username')
    email = request.form.get('email_adress')
    conf_thres = request.form.get('threshold')

    # More setting parameterw will be added HERE
    usr_setting = dict()
    usr_setting["username"] = usr_name
    usr_setting["threshold"] = conf_thres


    # Get path of user data & result
    usr_path = os.path.join(data_path, usr_name)
    usr_result_path = os.path.join(result_path, usr_name)

    # If this is new query, make directories
    if not os.path.exists(usr_path):
        os.makedirs(usr_path)
        print("!")
    if not os.path.exists(usr_result_path):
        os.makedirs(usr_result_path)

    with open(os.path.join(usr_path, 'setting.json'), 'w') as make_file:
        json.dump(usr_setting, make_file, indent='\t')
    with open(os.path.join(usr_path, 'setting.json'), 'w') as make_file:
        json.dump(usr_setting, make_file, indent='\t')

    # Save (image or video) files into the user data folder
    for i in range(len(files)):
        f = files[f'file[{i}]']
        f.save(os.path.join(usr_path, f.filename))

    print(f'All filed saved for the user {usr_name}')

    return ""


@app.route("/result/<query_id>",methods = ["GET"])
def get_results(query_id):
    
    global data_path
    global result_path

    # query_id = username
    usr_data_path = os.path.join(data_path, query_id)
    usr_result_path = os.path.join(result_path, query_id) 

    # Get images' path from user result directory
    url_lst = [f'results/{query_id}/{i}' for i in os.listdir(usr_data_path)]

    # Check if the number of image (file) is same between data and result folder
    # Note that video files are converted to frames and removed
    if len(os.listdir(usr_data_path)) == len(os.listdir(usr_result_path)):
        return render_template('result.html', query_id=query_id, url_lst = url_lst)
    else:
        return wait_template(query_id)


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=5002)
