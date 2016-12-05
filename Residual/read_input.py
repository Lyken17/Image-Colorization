"""
Helper functions for read input
"""

import os

import cv2

from config import *


def init_file_path(directory):
    """
    Get the image file path array
    :param directory: the directory that store images
    :return: an array of image file path
    """
    paths = []
    for file_name in os.listdir(directory):
        # Skip files that is not jpg
        if not file_name.endswith('.jpg'):
            continue
        file_path = '%s/%s' % (directory, file_name)
        if debug:
            paths.append(file_path)
        else:
            img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            # Throw gray space images
            if len(img.shape) == 3 and img.shape[2] != 1:
                paths.append(file_path)
    return paths


def read_image(filename_queue):
    """
    Read and store image with RGB color space
    :param filename_queue: the filename queue for image files
    :return: image with RGB color space
    """
    # Read the image with RGB color space
    reader = tf.WholeFileReader()
    key, content = reader.read(filename_queue)
    rgb_image = tf.image.decode_jpeg(content, channels=3, name="decoded_jpg")
    # Resize image to the right image_size
    rgb_image = tf.image.resize_images(rgb_image, [image_size, image_size], method=input_resize_method)
    # Make pixel element value in [0, 1)
    rgb_image = tf.div(tf.cast(rgb_image, tf.float32), 255, name="float_image")
    return rgb_image


def input_pipeline(filenames, b_size, num_epochs=None, shuffle=False):
    """
    Use a queue that randomizes the order of examples and return batch of images
    :param filenames: filenames
    :param b_size: batch size
    :param num_epochs: number of epochs for producing each string before generating an OutOfRange error
    :param shuffle: if true, the strings are randomly shuffled within each epoch
    :return: a batch of yuv_images
    """
    filename_queue = tf.train.string_input_producer(filenames, num_epochs=num_epochs, shuffle=shuffle)
    yuv_image = read_image(filename_queue)
    min_after_dequeue = dequeue_buffer_size
    capacity = min_after_dequeue + 3 * b_size
    image_batch = tf.train.shuffle_batch([yuv_image],
                                         batch_size=b_size,
                                         capacity=capacity,
                                         min_after_dequeue=min_after_dequeue)
    return image_batch