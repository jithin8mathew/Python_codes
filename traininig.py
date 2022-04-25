#!pip install -q tflite-model-maker
#!pip install tflite_support_nightly

import numpy as np
import os

from tflite_model_maker.config import ExportFormat
from tflite_model_maker import model_spec
from tflite_model_maker import object_detector

import tensorflow as tf
assert tf.__version__.startswith('2')

tf.get_logger().setLevel('ERROR')
from absl import logging
logging.set_verbosity(logging.ERROR)

use_custom_dataset = True
dataset_is_split = True

if use_custom_dataset:
	
	label_map = {1: 'SP'} 

	if dataset_is_split:
	    # If your dataset is already split, specify each path:
		train_images_dir = 'F:\\ABEN\\Soy_pod_count_project\\preprocessing\\EffDet_dataset\\train\\images'
		train_annotations_dir = 'F:\\ABEN\\Soy_pod_count_project\\preprocessing\\EffDet_dataset\\train\\annotations'
		val_images_dir = 'F:\\ABEN\\Soy_pod_count_project\\preprocessing\\EffDet_dataset\\validation\\images'
		val_annotations_dir = 'F:\\ABEN\\Soy_pod_count_project\\preprocessing\\EffDet_dataset\\validation\\annotations'
		test_images_dir = 'F:\\ABEN\\Soy_pod_count_project\\preprocessing\\EffDet_dataset\\test\\images'
		test_annotations_dir = 'F:\\ABEN\\Soy_pod_count_project\\preprocessing\\EffDet_dataset\\test\\annotations'
	else:
		# If it's NOT split yet, specify the path to all images and annotations
		images_in = 'dataset/images'
		annotations_in = 'dataset/annotations'
	  

if use_custom_dataset:
	if dataset_is_split:
		train_data = object_detector.DataLoader.from_pascal_voc(train_images_dir, train_annotations_dir, label_map=label_map)
		validation_data = object_detector.DataLoader.from_pascal_voc(val_images_dir, val_annotations_dir, label_map=label_map)
		test_data = object_detector.DataLoader.from_pascal_voc(test_images_dir, test_annotations_dir, label_map=label_map)
	else:
		train_dir, val_dir, test_dir = split_dataset(images_in, annotations_in, val_split=0.2, test_split=0.2, out_path='split-dataset')
		train_data = object_detector.DataLoader.from_pascal_voc(os.path.join(train_dir, 'images'),os.path.join(train_dir, 'annotations'), label_map=label_map)
		validation_data = object_detector.DataLoader.from_pascal_voc(os.path.join(val_dir, 'images'),os.path.join(val_dir, 'annotations'), label_map=label_map)
		test_data = object_detector.DataLoader.from_pascal_voc(os.path.join(test_dir, 'images'),os.path.join(test_dir, 'annotations'), label_map=label_map)
    
	print(f'train count: {len(train_data)}')
	print(f'validation count: {len(validation_data)}')
	print(f'test count: {len(test_data)}')


spec = object_detector.EfficientDetLite4Spec()

spec = object_detector.EfficientDetSpec(
	model_name='efficientdet-lite4', 
	uri='https://tfhub.dev/tensorflow/efficientdet/lite4/feature-vector/2', 
	hparams={'max_instances_per_image': 8000})


spec.config.tflite_max_detections= 5000
spec.config.max_instances_per_image = 2500

model = object_detector.create(train_data=train_data, 
								model_spec=spec, 
								validation_data=validation_data, 
								epochs=300, 
								batch_size=4, 
								train_whole_model=False)

model.evaluate(test_data)

TFLITE_FILENAME = 'efficientdet-lite-soypod.tflite'
LABELS_FILENAME = 'labels.txt'

model.export(export_dir='.', tflite_filename=TFLITE_FILENAME, label_filename=LABELS_FILENAME, export_format=[ExportFormat.TFLITE, ExportFormat.LABEL])