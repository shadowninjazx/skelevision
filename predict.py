# TRAINING CODE FOR SKELEVISION
# NOVEMBER 2021

'''
IMPORT LIBRARIES
'''
from argparse import ArgumentParser
import os
import torch, torchvision
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()
from detectron2.engine import DefaultPredictor, DefaultTrainer
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer, ColorMode
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2 import model_zoo
from detectron2.data.datasets import register_coco_instances

import matplotlib.pyplot as plt
import numpy as np
import cv2
from tqdm import tqdm
import csv
from math import atan2, cos, sin, sqrt, pi
import json
import glob


'''
TRAINING FUNCTION
'''
def predict():

    device = torch.device(f"cuda:{args.gpu}" if torch.cuda.is_available() else "cpu")
    print('using', device)

    ###############
    # ROI THRESHOLD DEFAULT=.8
    TH = .3
    # NMS THRESHOLD DEFAULT=.5
    NMS = .5
    ###############

    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    cfg.DATASETS.TEST = ()
    cfg.TEST.EVAL_PERIOD = 100
    cfg.DATALOADER.NUM_WORKERS = 2
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")  # Let training initialize from model zoo
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 512
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 19
    cfg.OUTPUT_DIR = args.checkpoint
    cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")

    register_coco_instances("test_ignore", {}, args.annotation, args.directory)
    cfg.DATASETS.TEST = ("test_ignore", )
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = TH   
    cfg.MODEL.ROI_HEADS.NMS_THRESH_TEST = NMS
    predictor = DefaultPredictor(cfg)
    dataset_dicts = DatasetCatalog.get("test_ignore")
    MetadataCatalog.get("test_ignore").thing_colors = [(244,67,54), (233,30,99), (156,39,176), (103,58,183), (63,81,181), (33,150,243), (3,169,244), (0,188,212), (0,150,136), (76,175,80), (139,195,74), (205,220,57), (255,235,59), (255,193,7), (255,152,0), (255,87,34), (121,85,72), (158,158,158), (96,125,139)]
    test_metadata = MetadataCatalog.get("test_ignore")

    '''SET INPUT AND OUTPUT DIRECTORIES'''
    # INPUT DIRECTORY
    in_dir = args.directory
    img_list = glob.glob(in_dir + '*.jpg')
    # OUTPUT DIRECTORY
    out_dir = args.output
    # CSV OUTPUT ADDR
    out_addr = f'{args.output}/measurements.csv'
    # JSON OUT ADDR
    json_out = f'{args.output}/measurements.json'
    # SEG IMAGES OUTPUT DIR
    dump_dir = f'{args.output}/segmentation_dump/'

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    else:
        pass
    if not os.path.exists(dump_dir):
        os.mkdir(dump_dir)
    else:
        pass

    '''DEFINE CLASS VARIABLES'''
    class_list = ['carpometacarpus','coracoid','femur','fibula','furcula','humerus','keel','metacarpal_4','metatarsus','other','radius','sclerotic_ring','second_digit_p_1','second_digit_p_2','skull','sternum','tarsus','ulna','not_bone']
    csv_columns = ['bone_id', 'keel-1', 'humerus-1', 'ulna-1', 'radius-1', 'carpometacarpus-1',
                'femur-1', 'tarsus-1', 'metatarsus-1', 'sclerotic_ring-1', 'skull-1', 'second_digit_p_1-1']
    csv_list = []
    web_db_json = {}

    result_dict = {}
    for d in tqdm(img_list):
        rgb = cv2.imread(d)
        img = cv2.resize(rgb, (1368, 912))
        boneid = d.replace(in_dir,'').replace('.jpg','')
        
        scores = {'keel':0, 'humerus':0, 'ulna':0, 'radius':0, 'carpometacarpus':0, 'femur':0, 'tarsus':0, 'metatarsus':0,
                    'sclerotic_ring':0, 'skull':0, 'second_digit_p_1':0}
        bid = boneid.replace('skeleton-','')
        meas = {'bone_id':bid}
        
        temp_db = {}
        for c in class_list:
            temp_db[c] = []
        
        outputs = predictor(img)
        fields = outputs['instances'].to('cpu').get_fields()
        seg_counter = 1
        
        '''VISUALIZE BIG IMAGE'''
        v2 = Visualizer(img[:, :, ::-1], metadata=test_metadata, scale=1, instance_mode=ColorMode.SEGMENTATION)
        pred_out = v2.draw_instance_predictions(outputs["instances"].to("cpu"))
        target_dir = dump_dir + f'{bid}/'
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)
        cv2.imwrite(target_dir + 'det.jpg', pred_out.get_image()[:, :, ::-1], [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        cv2.imwrite(target_dir + 'rgb.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        
        for boxi in range(len(fields['pred_boxes'])):
            
            '''EXTRACT SEGMENTATION INFORMATION'''
            pred_class = fields['pred_classes'][boxi].tolist()
            pred_prob = fields['scores'][boxi].tolist()
            points = fields['pred_boxes'][boxi]
            x1, y1, x2, y2 = points.tensor.tolist()[0]
            class_name = class_list[pred_class]
            sub_prob = fields['pred_masks'][boxi].to(torch.uint8).numpy()[int(y1):int(y2),int(x1):int(x2)]
            sub_prob = cv2.resize(sub_prob, (sub_prob.shape[1], sub_prob.shape[0]), cv2.INTER_CUBIC)
            
            '''SEGMENTATION NAMING'''
            seg_name = f'{seg_counter:02d}_{class_name}'
            
            '''CREATE MASKED RBG IMAGE'''
            sub_rgb = rgb[int(y1):int(y2),int(x1):int(x2)]
            sub_rgb = cv2.bitwise_and(sub_rgb, sub_rgb, mask=sub_prob)
            sub_rgb[sub_prob == 0] = (99, 99, 99)
            
            '''CONCATENATE ALL CONTOURS'''
            contours, hierarchy = cv2.findContours(sub_prob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            max_area = 0
            max_c = []
            for ix, c in enumerate(contours):
                if ix == 0:
                    max_c = c
                else:
                    max_c = np.vstack((max_c, c))
            
            '''PCA'''
            try:
                sz = len(max_c)
                data_pts = np.empty((sz, 2), dtype=np.float64)
                for iy in range(data_pts.shape[0]):
                    data_pts[iy,0] = max_c[iy,0,0]
                    data_pts[iy,1] = max_c[iy,0,1]
                mean = np.empty((0))
                mean, eigenvectors, eigenvalues = cv2.PCACompute2(data_pts, mean)
                cntr = (int(mean[0,0]), int(mean[0,1]))
                angle = atan2(eigenvectors[0,1], eigenvectors[0,0])
            except:
                continue

            '''ROTATE PCA'''
            b_size = int(sub_rgb.shape[0]*.5)
            mask_img = cv2.copyMakeBorder(sub_rgb, b_size, b_size, b_size, b_size, cv2.BORDER_CONSTANT, None, (99,99,99))
            center=tuple(np.array([mask_img.shape[0], mask_img.shape[1]])/2)
            rot_mat = cv2.getRotationMatrix2D(center, (angle*180/pi), 1.0)
            if mask_img.shape[0] > mask_img.shape[1]:
                seg_side = int(mask_img.shape[0]*1)
            else:
                seg_side = int(mask_img.shape[1]*1)

            mask_img = cv2.warpAffine(mask_img, rot_mat, (seg_side,seg_side), borderMode=cv2.BORDER_CONSTANT, 
                                        borderValue=(99,99,99))
            
            '''ROTATE PCA FOR PROB'''
            b_size = int(sub_prob.shape[0]*.5)
            sub_prob = cv2.copyMakeBorder(sub_prob, b_size, b_size, b_size, b_size, cv2.BORDER_CONSTANT, None, (0,0,0))
            center=tuple(np.array([sub_prob.shape[0], sub_prob.shape[1]])/2)
            rot_mat = cv2.getRotationMatrix2D(center, (angle*180/pi), 1.0)
            if sub_prob.shape[0] > sub_prob.shape[1]:
                seg_side = int(sub_prob.shape[0]*1)
            else:
                seg_side = int(sub_prob.shape[1]*1)

            sub_prob = cv2.warpAffine(sub_prob, rot_mat, (seg_side,seg_side))
            
            '''EXTRACT LENGTH'''
            contours, hierarchy = cv2.findContours(sub_prob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            max_area = 0
            max_c = []
            for ix, c in enumerate(contours):
                if ix == 0:
                    max_c = c
                else:
                    max_c = np.vstack((max_c, c))
            try:
                leftmost = tuple(max_c[max_c[:,:,0].argmin()][0])
                rightmost = tuple(max_c[max_c[:,:,0].argmax()][0])
                topmost = tuple(max_c[max_c[:,:,1].argmin()][0])
                bottommost = tuple(max_c[max_c[:,:,1].argmax()][0])
            except:
                continue
            
            px_dist = np.sqrt(np.square(leftmost[0] - rightmost[0]) + np.square(leftmost[1] - rightmost[1]))
            mm_dist = (px_dist / 110 * 25.4)
            str_dist = '{0:.2f}'.format(mm_dist)
            
            '''CROP IMAGE'''
            br = cv2.boundingRect(max_c)
            border = 0
            mask_img = mask_img[br[1]-border:br[1]+br[3]+border, br[0]-border:br[0]+br[2]+border]
            
            if class_name in scores:
                if pred_prob > scores[class_name]:
                    scores[class_name] = pred_prob
                    meas[f'{class_name}-1'] = str_dist
                    
            '''DUMP IMAGE'''
            target_dir = dump_dir + f'{bid}/'
            if not os.path.isdir(target_dir):
                os.makedirs(target_dir)
            
            target_addr = target_dir + f'{seg_name}.jpg'
            cv2.imwrite(target_addr, mask_img)
            
            
            temp_db[class_list[pred_class]].append({"name":seg_name,"dist_0":str_dist,"bprob":pred_prob})
            seg_counter += 1
        
        csv_list.append(meas)
        web_db_json[boneid] = temp_db
        

    with open(out_addr, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in csv_list:
            writer.writerow(data)

    with open(json_out, 'w') as fp:
        json.dump(web_db_json, fp)

    print('Predictions saved:', len(web_db_json))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-c", "--checkpoint", metavar="path", type=str, help="path to model checkpoint", required=True)
    parser.add_argument("-d", "--directory", metavar="path", type=str, help="directory to images", required=True)
    parser.add_argument("-o", "--output", default='output', metavar="path", type=str, help="path to save the predictions", required=False)
    parser.add_argument("-g", "--gpu", default=0, metavar='num', help="gpu id", required=False)
    parser.add_argument("-a", "--annotation", metavar="path", type=str, help="path to coco annotation json", required=True)
    args = parser.parse_args()

    predict()