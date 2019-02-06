# Object Detection using SSD512(Single Shot Multibox Detector)

# Libraries
from keras import backend as K
from keras.preprocessing import image
from keras.optimizers import Adam
import imageio
import numpy as np
import os
import cv2

# Dependencies
from models.keras_ssd512 import ssd_512
from keras_loss_function.keras_ssd_loss import SSDLoss

# Defining the width and height of the image
height = 512
width = 512

# Defining confidence threshold
confidence_threshold = 0.5

# Different Classes of objects in VOC dataset
classes = ['background',
           'aeroplane', 'bicycle', 'bird', 'boat',
           'bottle', 'bus', 'car', 'cat',
           'chair', 'cow', 'diningtable', 'dog',
           'horse', 'motorbike', 'person', 'pottedplant',
           'sheep', 'sofa', 'train', 'tvmonitor']


K.clear_session() # Clear previous models from memory.

# creating model and loading pretrained weights
model = ssd_512(image_size=(height, width, 3),	# dimensions of the input images (fixed for SSD512)
                n_classes=20,	# Number of classes in VOC 2007 & 2012 dataset
                mode='inference',
                l2_regularization=0.0005,
                scales=[0.07, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.05], 
                aspect_ratios_per_layer=[[1.0, 2.0, 0.5],
                                         [1.0, 2.0, 0.5, 3.0, 1.0/3.0],
                                         [1.0, 2.0, 0.5, 3.0, 1.0/3.0],
                                         [1.0, 2.0, 0.5, 3.0, 1.0/3.0],
                                         [1.0, 2.0, 0.5, 3.0, 1.0/3.0],
                                         [1.0, 2.0, 0.5],
                                         [1.0, 2.0, 0.5]],
               two_boxes_for_ar1=True,
               steps=[8, 16, 32, 64, 128, 256, 512],
               offsets=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
               clip_boxes=False,
               variances=[0.1, 0.1, 0.2, 0.2],
               normalize_coords=True,
               subtract_mean=[123, 117, 104],
               swap_channels=[2, 1, 0],
               confidence_thresh=0.5,
               iou_threshold=0.45,
               top_k=200,
               nms_max_output_size=400)

# path of the pre trained model weights 
weights_path = 'weights/VGG_VOC0712Plus_SSD_512x512_ft_iter_160000.h5'
model.load_weights(weights_path, by_name=True)

# Compiling the model 
adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)
ssd_loss = SSDLoss(neg_pos_ratio=3, alpha=1.0)
model.compile(optimizer=adam, loss=ssd_loss.compute_loss)


# Paths of input and output inages
input_image_path = 'inputs/images'
output_image_path = 'outputs/images'

# Function to detect objects in image
def detect_object(input_image, original_image):
	original_image_height, original_image_width = original_image.shape[:2]
	y_pred = model.predict(input_image)
	actual_prediction = [y_pred[k][y_pred[k,:,1] > confidence_threshold] for k in range(y_pred.shape[0])]
	for box in actual_prediction[0]:
		# Coordinates of diagonal points of bounding box
		x0 = box[-4] * original_image_width / width
		y0 = box[-3] * original_image_height / height
		x1 = box[-2] * original_image_width / width
		y1 = box[-1] * original_image_height / height
		label_text = '{}: {:.2f}'.format(classes[int(box[0])], box[1])	# label text
		cv2.rectangle(original_image, (int(x0), int(y0)), (int(x1), int(y1)), (255, 0, 0), 2)	# drwaing rectangle
		cv2.putText(original_image, label_text, (int(x0), int(y0)), cv2.FONT_HERSHEY_DUPLEX, 1.4, (255, 255, 255), 2, cv2.LINE_AA) # putting lable
	return original_image
	

# Detecting objects in images
for file in os.listdir(input_image_path):
	print('Reading', file)  
	input_image = image.load_img(os.path.join(input_image_path, file), target_size=(height, width))	#  Reading image as 512*512 size
	input_image = image.img_to_array(input_image)	# converting to array
	input_image = np.reshape(input_image, (1, 512, 512, 3)) #expanding dimension
	original_image = imageio.imread(os.path.join(input_image_path, file))	# original image for box purpose
	if input_image is not None:
		output_image = detect_object(input_image, original_image)	# detecting objects
		imageio.imwrite(os.path.join(output_image_path, file), output_image[:, :, :])	# savinng back images
		
		
# TODO make video support also

