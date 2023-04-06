import torch
import cv2, os, time, csv, torchvision
import torchvision.transforms.functional as TF
import numpy as np
import mimetypes
from natsort import natsorted
import smtplib
from email.mime.text import MIMEText

# Detectron2 for inference
from detectron2.config import get_cfg
from detectron2.modeling import build_model
from detectron2.checkpoint import DetectionCheckpointer
from detectron2 import model_zoo

# You may need to restart your runtime prior to this, to let your installation take effect
# Some basic setup
# Setup detectron2 logger
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common libraries
import matplotlib.pyplot as plt
import cv2

# import some common detectron2 utilities
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog

from detectron2.engine import DefaultTrainer
from detectron2.config import get_cfg
import os, json

from sahi_inference import build_detection_model, batch_inference
from utils import send_email, vid_to_fr, parse_bbox_info

# Server's main run
if __name__ == '__main__':
    import time
    import pandas as pd
    import sqlite3

    while True:
        # Read sqlite query results into a pandas DataFrame
        con = sqlite3.connect("db.sqlite")

        task_df = pd.read_sql_query("SELECT * from task_table", con)
        user_df = pd.read_sql_query("SELECT * from user_table", con)
        print(task_df)
        print(user_df)

        for id in range(len(task_df.index)): # Get id to parse data row by row
            task_stage = task_df.iloc[id]['process_stage']  # Return 0(=False) or 1(=True) value
            if not task_stage =='done':

                con.execute("UPDATE task_table SET process_stage = ? Where id = ?", ('being_processed', id+1))
                con.commit()

                # Parse the information of current task
                user_name = task_df.iloc[id]['user_name']
                task_name = task_df.iloc[id]['task_name']
                threshold = int(task_df.iloc[id]['sensitivity'])/100

                data_path = os.path.join('./static/user_data', user_name, task_name)
                visual_path = task_df.iloc[id]['visual_path']  # Equals to 'project' parameter of sahi predict function, thus will saved in .../visual_path/exp/visuals
                
                video_name_lst = os.listdir(data_path)
                video_path_lst = [os.path.join(data_path, i) for i in video_name_lst]
                result_path_lst = [os.path.join(visual_path, i) for i in video_name_lst]

                detection_model = build_detection_model('./model_25.pth', confidence_threshold=threshold)  # Hard-coded !!!

                # Convert uploaded videos into frames in img_src
                for vid_path, vid_name, result_path in zip(video_path_lst, video_name_lst, result_path_lst):
                    vid_to_fr(vid_path)    
                    batch_inference(vid_path, detection_model, 'temp_result', f'{user_name}/{task_name}/{vid_name}')

                    os.system(f"mv ./temp_result/{user_name}/{task_name}/{vid_name}/pickles/* {result_path}")
                    os.system(f"mv ./temp_result/{user_name}/{task_name}/{vid_name}/visuals/* {result_path}")
                    os.system(f"rm -r temp_result")


                # Make .csv file for ordering/filtering in front-end
                for result_path in result_path_lst:
                    # Sort image and pickle files in a correct way
                    result_img_lst = natsorted([i for i in os.listdir(result_path) if i.endswith('.jpg')])
                    pickle_lst = natsorted([i for i in os.listdir(result_path) if i.endswith('.pickle')])

                    print(pickle_lst)
                    # Get the number of bounding boxes & maximum confidence for all images in one video folder
                    parsed_data = [parse_bbox_info(os.path.join(result_path, i)) for i in pickle_lst]
                    print(parsed_data)
                    num_of_bbox_lst = [i[0] for i in parsed_data]
                    max_score_lst = [i[1] for i in parsed_data]
                    print(num_of_bbox_lst)
                    print(max_score_lst)
                    # Convert parsed data to tuples to be written by csv writer
                    csv_lines = zip(result_img_lst, num_of_bbox_lst, max_score_lst)

                    # Write .csv file
                    out_file = open(f'{result_path}/metadata.csv', 'w', newline='')
                    writer = csv.writer(out_file)
                    header = ['name', 'bbox_num', 'confidence']
                    writer.writerow(header)
                    for line in csv_lines:
                        writer.writerow(line)
                    out_file.close()


                con.execute("UPDATE task_table SET process_stage = ? Where id = ?", ('done', id+1))
                con.commit()

                c = con.cursor()

                if '%40' in user_name:
                    user_email = user_name.replace('%40', '@')
                else:
                    c.execute('SELECT email FROM user_table WHERE userid = ?', (user_name,))
                    user_email = str(c.fetchall()[0][0])
                print(user_email, type(user_email))
                
                send_email(user_name, user_email, task_name, info_type='finish')
        con.close()       
        time.sleep(10)