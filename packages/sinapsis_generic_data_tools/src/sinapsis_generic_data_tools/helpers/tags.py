# -*- coding: utf-8 -*-
from enum import Enum


class Tags(Enum):
    AGGREGATOR = "aggregator"
    BUFFER = "buffer"
    COLOR = "color"
    CONVERSION = "color_conversion"
    HISTORY = "history"
    IMAGE = "image"
    SEGMENTATION = "segmentation"
    ROI = "region_of_interest"
    MASK = "mask"
    SPACE = "color_space"
    QUEUE = "queue"
