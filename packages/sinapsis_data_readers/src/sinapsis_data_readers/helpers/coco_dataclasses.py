# -*- coding: utf-8 -*-
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class CocoJsonKeys:
    """
    Keys to access the annotations dictionary in coco format
        IMAGES (str): Key to access the 'images' entry.
        FILE_NAME (str): Key to access the 'file_name' entry.
        IMAGE_ID (str): Key to access the 'image_id' entry.
        COCO_LICENSE (str): Key to access the 'coco_license' entry.
        COCO_URL (str): Key to access the 'coco_url' entry.
        HEIGHT (str): Key to access the 'height' entry.
        WIDTH (str): Key to access the 'width' entry.
        DATE (str): Key to access the 'date' entry.
        ANNOTATIONS (str): Key to access the 'annotations' entry.
    """

    IMAGES: str = "images"
    FILE_NAME: str = "file_name"
    IMAGE_ID: str = "id"
    COCO_LICENSE: str = "license"
    COCO_URL: str = "coco_url"
    HEIGHT: str = "height"
    WIDTH: str = "width"
    DATE: str = "date_captured"
    ANNOTATIONS: str = "annotations"


@dataclass(frozen=True)
class CocoAnnotationsKeys:
    """
    Keys to access the annotations fields in the coco-format annotations
        IMAGE_ID (str): key to access the 'image_id' field.
        SEGMENTATIONS (str): key to access the 'segmentations' field.
        BBOX (str): key to access the 'bbox' field.
        ORIENTED_BBOX (str): key to access the 'oriented_bbox' field.
        ANNOTATION_ID (str): key to access the 'annotation_id' field.
        AREA (str): key to access the 'area' field.
        CATEGORY_ID (str): key to access the 'category_id' field.
        IS_CROWD (str): key to access the 'is_crowd' field.
        NUM_KEYPOINTS (str): key to access the 'num_keypoints' field.
        KEYPOINTS (str): key to access the 'keypoints' field.
        SEGMENTS_INFO (str): key to access the 'segments_info' field.
        SCORE (str): key to access the 'score' field.
    """

    IMAGE_ID: str = "image_id"
    SEGMENTATIONS: str = "segmentation"
    BBOX: str = "bbox"
    ORIENTED_BBOX: str = "oriented_bbox"
    ANNOTATION_ID: str = "id"
    AREA: str = "area"
    CATEGORY_ID: str = "category_id"
    IS_CROWD: str = "iscrowd"
    NUM_KEYPOINTS: str = "num_keypoints"
    KEYPOINTS: str = "keypoints"
    SEGMENTS_INFO: str = "segments_info"
    SCORE: str = "score"
