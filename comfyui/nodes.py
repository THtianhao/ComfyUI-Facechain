# Copyright (c) Alibaba, Inc. and its affiliates.
import json
import os

import cv2
import numpy as np
import torch
from PIL import Image
from diffusers import StableDiffusionPipeline, StableDiffusionControlNetPipeline, ControlNetModel, \
    UniPCMultistepScheduler
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from torch import multiprocessing
from transformers import pipeline as tpipeline

import pydevd_pycharm
pydevd_pycharm.settrace('49.7.62.197', port=10090, stdoutToServer=True, stderrToServer=True)
from .model_holder import *
from .utils.img_utils import *

class FCStyleLoraLoad:
    @classmethod
    def INPUT_TYPES(s):
        return {}

    FUNCTION = "style_lora_load"
    CATEGORY = "facechain/lora"

    def style_lora_load(self):
        return ()

class FCLoraMerge:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "merge_lora_first": ("MODEL",),
                "merge_lora_second": ("MODEL",),
                "multiplier": ("FLOAT", {"default": 0.5, "min": 0, "max": 1, "step": 0.1})
            }
        }

    RETURN_TYPES = ("MODEL",)
    RETURN_NAMES = ("lora",)
    FUNCTION = "merge_lora"
    CATEGORY = "facechain/lora"

    def retain_face(self, merge_lora_first, merge_lora_second):
        # pipe = StableDiffusionPipeline.from_pretrained(base_model_path, safety_checker=None, torch_dtype=torch.float32)
        # merge_lora()
        return ()

class FCLoraStyle:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "merge_lora_first": ("MODEL",),
            }
        }

    RETURN_TYPES = ("MODEL",)
    RETURN_NAMES = ("style_lora",)
    FUNCTION = "lora_style"
    CATEGORY = "facechain/lora"

    def lora_style(self, image):
        return (image,)

class FCFaceFusion:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "source_image": ("IMAGE",),
                "fusion_image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "image_face_fusion"
    CATEGORY = "facechain/model"

    def image_face_fusion(self, source_image, fusion_image):
        source_image = tensor_to_img(source_image)
        fusion_image = tensor_to_img(fusion_image)
        result_image = get_image_face_fusion()(dict(template=source_image, user=fusion_image))[OutputKeys.OUTPUT_IMG]
        result_image = Image.fromarray(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
        return (img_to_tensor(result_image),)

class FCFaceDetection:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "source_image": ("IMAGE",),
                "face_index": ("INT", {"default": 0, "min": 0, "max": 10, "step": 1})
            }
        }

    RETURN_TYPES = ("IMAGE", "BOX",)
    FUNCTION = "face_detection"
    CATEGORY = "facechain/model"

    def face_detection(self, source_image, face_index):
        pil_source = tensor_to_img(source_image)
        result_dec = get_face_detection()(pil_source)
        keypoints = result_dec['keypoints']
        boxes = result_dec['boxes']
        scores = result_dec['scores']
        keypoint = keypoints[face_index]
        score = scores[face_index]
        box = boxes[face_index]
        box = np.array(box, np.int32)
        crop_result = source_image[:, box[1]:box[3], box[0]:box[2], :]
        return (crop_result, box)
