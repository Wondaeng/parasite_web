import torch
import cv2, os, time
import os, cv2, torchvision
import torchvision.transforms.functional as TF
import numpy as np
import mimetypes
from natsort import natsorted

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
import numpy as np
import cv2

# import some common detectron2 utilities
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog

from detectron2.engine import DefaultTrainer
from detectron2.config import get_cfg
import os, json



# Currently only one parameter
def parse_parameters(task_pth):
    json_pth = os.path.join(task_pth, 'setting.json')
    with open(json_pth, 'r') as f:
        json_data = json.load(f)
    threshold = int(json_data['threshold']) / 100
    os.system(f"rm {json_pth}")
    return threshold


def build_predictor(weights='model_best.pth', num_classes=1, threshold=0.8):
    # Loading pre-trained model (Pytorch)
    '''weights = FasterRCNN_ResNet50_FPN_Weights.DEFAULT
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights = weights)'''
    # Loading parasite trained model and wrap it with predictor
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = num_classes
    cfg.MODEL.WEIGHTS = weights
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = threshold
    predictor = DefaultPredictor(cfg)
    return predictor


# Run inference with given predictor
def inference(task_pth, file_name, save_pth, predictor):
    img = cv2.imread(os.path.join(task_pth, file_name))
    outputs = predictor(img)
    v = Visualizer(img[:, :, ::-1], scale=1.0)
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    out.save(save_pth)
    return None


def vid_to_fr(task_pth, n=20):
    for file in os.listdir(task_pth):
        file_path = os.path.join(task_pth, file)
        if mimetypes.guess_type(file_path)[0].startswith('video'): # If the file is video
            
            # Extract frames from video using cv2
            video = cv2.VideoCapture(file_path)
            
            count = 0
            success = True
            while(success):
                success, image = video.read()
                if(int(video.get(1)) % n == 0): # extract 1 frame per n frames
                    save_name = os.path.splitext(file_path)[0]
                    cv2.imwrite(f'{save_name}_f{count}.jpg', image)
                    print('Saved frame number :', str(int(video.get(1))))
                    count += 1
                
            video.release()
            os.system(f"rm {file_path}") # Currently ERROR here if a space in a file name
    return None

# Below section is for the case when using Pytorch for the inference    
'''def draw_boxes(result, orig, save_pth, threshold=0.7):
    result = result[0]
    COLORS = np.random.uniform(0, 255, size=(1000, 3))
    for i in range(0, len(result["boxes"])):
        confidence = result["scores"][i]

        if confidence > threshold:
            idx = int(result["labels"][i])
            box = result["boxes"][i].detach().numpy()
            (startX, startY, endX, endY) = box.astype("int")

            label = f"{idx}: {confidence*100:.2f}"

            cv2.rectangle(orig, (startX, startY), (endX, endY), COLORS[idx], 3)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(orig, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS[idx], 3)

    cv2.imwrite(f"{save_pth}", orig)
    return None'''


# Server's main run
while True:
    dir_lst = os.listdir('./static/results')
    print(dir_lst)
    for usr in dir_lst:
        usr_data_pth = os.path.join('./static/user_data', usr)
        usr_result_pth = os.path.join('./static/results', usr)
        tasks = os.listdir(usr_data_pth)
        print(tasks)
        for task in tasks:
            task_data_pth = os.path.join(usr_data_pth, task)
            task_result_pth = os.path.join(usr_result_pth, task)
            infer_lst = os.listdir(task_result_pth)
            print(infer_lst)
            if len(infer_lst) == 0:
                print(f"Start inference for {task_data_pth}")
                threshold = parse_parameters(task_data_pth)
                print(threshold)
                vid_to_fr(task_data_pth)            
                imgs_data = os.listdir(task_data_pth)
                predictor = build_predictor(threshold = threshold)
                for img_data in natsorted(imgs_data):
                    print("3")
                    save_pth = os.path.join(task_result_pth, img_data)
                    outputs = inference(task_data_pth, img_data, save_pth, predictor)
            else:
                pass
        print('sleep')
    time.sleep(5)
