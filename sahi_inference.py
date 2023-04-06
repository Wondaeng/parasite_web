from sahi import AutoDetectionModel
from sahi.predict import predict
from sahi.utils.cv import read_image_as_pil
from sahi.utils.detectron2 import export_cfg_as_yaml

from detectron2.modeling import build_model
from detectron2.config import get_cfg
from detectron2 import model_zoo
import pickle

import torch, torchvision
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from collections import OrderedDict
# def build_detection_model(weight_path, config_path, model_type = 'detectron2', confidence_threshold = 0.7):
#     cfg = get_cfg()
#     cfg.merge_from_file(model_zoo.get_config_file(config_path))
#     cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = confidence_threshold
#     cfg.MODEL.WEIGHTS = weight_path # Set path model .pth
#     cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
#     cfg.MODEL.DEVICE = "cuda"

#     export_cfg_as_yaml(cfg, "config.yaml")

#     return AutoDetectionModel.from_pretrained(
#         model_type = model_type,
#         model_path = weight_path,
#         config_path = 'config.yaml',
#         confidence_threshold = confidence_threshold,
#         category_mapping= {"0":"parasite"}
#     )

def build_detection_model(weight_path, model_type = 'torchvision', confidence_threshold = 0.7):
    checkpoint = torch.load(weight_path)

    model_name = "fasterrcnn_resnet50_fpn"
    weights = None
    weights_backbone = None
    num_classes = 2
    kwargs = {}

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    state_dict = checkpoint["model"]

    new_layer_keys = [i.replace('0.weight', 'weight').replace('0.bias', 'bias') if "backbone.fpn" in i else i for i in state_dict.keys() ]
    new_layer_keys = [i.replace('0.0.weight', 'weight').replace('0.0.bias', 'bias') if "rpn.head.conv" in i else i for i in new_layer_keys]

    for (old_key, old_val), new_key in zip(list(state_dict.items()), new_layer_keys):
        del state_dict[old_key]
        state_dict[new_key] = old_val

    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
        pretrained=False, 
        progress=True, 
        num_classes=num_classes, 
        pretrained_backbone=False, 
        trainable_backbone_layers=None, 
        **kwargs
        )

    model.load_state_dict(state_dict)

    return AutoDetectionModel.from_pretrained(

        model_type = model_type,
        model = model,
        confidence_threshold = confidence_threshold,
        category_mapping= {"1":"parasite"}
    )

def batch_inference(image_src_path, detection_model, project, name, slice_height = 512, slice_width = 512, visual_bbox_thickness=1, visual_text_size=1.5):
    result = predict(
        source = image_src_path,  # Path of the directory with images to be inferenced
        detection_model = detection_model,
        slice_height = slice_height,
        slice_width = slice_width,
        overlap_height_ratio = 0.2,
        overlap_width_ratio = 0.2,
        model_category_mapping = {"0":"parasite"},
        visual_export_format = 'jpg',
        export_pickle = True,
        
        # Inference images (i.e., visuals) will be saved in project/name/visuals/
        # and this export_dir will be return as return_dict parameter is set as True
        project = project,
        name = name
    )

    return None

if __name__ == "__main__":  # Test sahi runs by running the script 
    detection_model = build_detection_model('./model_best.pth', "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml")
    batch_inference('./imgs', detection_model, './only/project')
