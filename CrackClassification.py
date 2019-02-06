""""
Onboard script for the AIY - Crack Classification project
Load the binary trained graph and label, initialize the camera, and run the classification at each inference
Turn on the RED led in case of crack, Green otherwise. 
Author: Benjamin IOLLER
""""

#!/usr/bin/env python3
import os

from picamera import PiCamera, Color

from aiy.vision import inference
from aiy.vision.models import utils

from gpiozero import LED
from aiy.pins import (PIN_A, PIN_B)

label_path = '/opt/aiy/models/'

def read_labels(label_path):
    with open(label_path) as label_file:
        return [label.strip() for label in label_file.readlines()]

def process(result, labels, tensor_name, threshold, top_k):
    """Processes inference result and returns labels sorted by confidence."""
    # MobileNet based classification model returns one result vector.
    assert len(result.tensors) == 1
    tensor = result.tensors[tensor_name]
    probs, shape = tensor.data, tensor.shape
    assert shape.depth == len(labels)
    pairs = [pair for pair in enumerate(probs) if pair[1] > threshold]
    pairs = sorted(pairs, key=lambda pair: pair[1], reverse=True)
    pairs = pairs[0:top_k]
    return [[labels[index], prob] for index, prob in pairs]


def main():
    # Loading the model and label
    model = inference.ModelDescriptor(
        name='mobilenet_based_classifier',
        input_shape=(1, 160, 160, 3),
        input_normalizer=(128.0, 128.0),
        compute_graph=utils.load_compute_graph('CrackClassification_graph.binaryproto'))
    print("Model loaded.")

    labels = read_labels(label_path + 'crack_label.txt')
    print("Labels loaded")
    
    # Classifier parameters
    top_k = 3
    threshold = 0.4
    num_frame = None
    show_fps = False
    
    # LED setup
    ledRED = LED(PIN_B)
    ledGREEN = LED(PIN_A)
    ledRED.off()
    ledGREEN.on()

    with PiCamera(sensor_mode=4, resolution=(1640, 1232), framerate=30) as camera:
        with inference.CameraInference(model) as camera_inference:
            for result in camera_inference.run(num_frame):
                processed_result = process(result, labels, 'final_result',threshold, top_k)
                    
                if processed_result[0][0] == 'positive':
                    print("CRACK")
                    ledGREEN.off()
                    ledRED.on()
                else:
                    print("CLEAR")
                    ledRED.off()
                    ledGREEN.on()
                
                print("Camera inference rate: " + str(camera_inference.rate))

if __name__ == '__main__':
    main()
