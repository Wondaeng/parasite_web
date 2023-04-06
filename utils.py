import mimetypes, smtplib
import os
import cv2
import pickle
import pandas as pd

from email.mime.text import MIMEText

def vid_to_fr(task_path, n=20):
    for file in os.listdir(task_path):
        file_path = os.path.join(task_path, file).replace(' ', '\ ')  # Handle the case when space in the task name
        
        if mimetypes.guess_type(file_path)[0].startswith('video'):  # If the file is video     
            # Extract frames from video using cv2
            video = cv2.VideoCapture(file_path)
            print(file_path)
            if video.isOpened():
                count = 0
                success = True
                while(success):
                    success, image = video.read()
                    if(int(video.get(1)) % n == 0) and success: # extract 1 frame per n frames
                        save_name = os.path.splitext(file_path)[0]
                        cv2.imwrite(f'{save_name}_f{count}.jpg', image)
                        print('Saved frame number :', str(int(video.get(1))))
                        count += 1
                
                video.release()
            os.system(f"rm {file_path}") # Currently ERROR here if a space in a file name

    return None


def send_email(user_name, user_email, task_name, info_type):
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login('trypa.screening@gmail.com', 'kyfwwjrnyypkhysw')
    
    if not user_name:  # If guest user
        if info_type == 'finish':
            msg_html = f"""\
                <html>
                    <head></head>

                    <body>
                        <p><b>Your task is finished!</b></p>
                        <p>Email: {user_email}</p>
                        <p>Task Name: {task_name}</p>
                        <p>Go to result section of the page after logged in.</p>
                        <p>http://223.194.227.150:5002</p>
                    </body>
                </html>
                """
            msg = MIMEText(msg_html, 'html')
            msg['Subject'] = 'ATS - Your Job is Finished!' 
        elif info_type =='submit':
            msg_html = f"""\
                <html>
                    <head></head>

                    <body>
                        <p><b>Your task is submitted!</b></p>
                        <p>Email: {user_email}</p>
                        <p>Task Name: {task_name}</p>
                        <p>Go to result section of the page after logged in.</p>
                        <p>http://223.194.227.150:5002</p>
                    </body>
                </html>
                """
            msg = MIMEText(msg_html, 'html')
            msg['Subject'] = 'ATS - Your Job is Submitted!' 
    else:  # If user logged in
        if info_type == 'finish':
            msg_html = f"""\
                <html>
                    <head></head>

                    <body>
                        <p><b>Your task is finished!</b></p>
                        <p>Email: {user_email}</p>
                        <p>Task Name: {task_name}</p>
                        <p>Go to result section of the page after logged in.</p>
                        <p>http://223.194.227.150:5002</p>
                    </body>
                </html>
                """
            msg = MIMEText(msg_html, 'html')
            msg['Subject'] = 'ATS - Your Job is Finished!' 
        elif info_type =='submit':
            msg_html = f"""\
                <html>
                    <head></head>

                    <body>
                        <p><b>Your task is submitted!</b></p>
                        <p>Email: {user_email}</p>
                        <p>Task Name: {task_name}</p>
                        <p>Go to result section of the page after logged in.</p>
                        <p>http://223.194.227.150:5002</p>
                    </body>
                </html>
                """
    
            msg = MIMEText(msg_html, 'html')
            msg['Subject'] = 'ATS - Your Job is Submitted!' 
    msg['To'] = user_email
    smtp.sendmail('trypa.screening@gmail.com', user_email, msg.as_string())
    smtp.quit()


# Return the number of bbox and highest confidence
# for each image (i.e., each prediction's .pickle file)
def parse_bbox_info(file_path):

    print(file_path)
    # Open .pickle file
    with open(file_path, "rb") as fr:
        data = pickle.load(fr)

    print(data)    
    # Get a list of scores (i.e., prediction confidence)
    score_lst = []
    for obj_prediction in data:
        score_lst.append(obj_prediction.score.value)

    print(score_lst)
    # Number of bounding box = Number of elements in score list
    num_bbox = len(score_lst)
    max_score = max(score_lst, default=0)

    return num_bbox, max_score