# -*- coding: utf-8 -*-

import numpy as np
from sinapsis_core.data_containers.annotations import BoundingBox


def bbox_xyxy_to_xywh(xyxy_bbox: np.ndarray) -> tuple[float, float, float, float]:
    """
    Converts the format for defining bounding boxes from xyxy to xywh

    Args:
        xyxy_bbox (np.ndarray): the bbox object in (x_min, y_min),
            (x_max, y_max) coordinates
    Returns:
        (tuple[float, float, float, float]) : the coordinates of the bbox
        in (x, y), (width and height) coordinates.
    """
    x = float(xyxy_bbox[0])
    y = float(xyxy_bbox[1])
    w = float(xyxy_bbox[2]) - x
    h = float(xyxy_bbox[3]) - y
    return x, y, w, h


def bbox_xywh_to_xyxy(xywh_bbox: BoundingBox) -> tuple[float, float, float, float]:
    """
    Converts the format for defining bounding boxes from xywh to xyxy

    Args:
        xywh_bbox (BoundingBox): The BoundingBox object in format x, y, w, h
    Returns:
        (tuple[float, float, float, float]): the coordinates of the bbox
            in x_min, y_min, x_max, y_max

    """
    x1 = float(xywh_bbox.x)
    y1 = float(xywh_bbox.y)
    x2 = float(xywh_bbox.w) + x1
    y2 = float(xywh_bbox.h) + y1
    return x1, y1, x2, y2


def bbox_iou_batch(boxes_a: np.ndarray, boxes_b: np.ndarray) -> np.ndarray:
    """Computes the Intersection over Union (IoU) metric.

    This method calculates the IoU for each pair of bounding boxes in
    'boxes_a' and 'boxes_b'. IoU measures the overlap between two bounding
    boxes as the ratio of their intersection area to their combined area.

    Args:
        boxes_a (np.ndarray): An array of shape '(N, 4)' representing N bounding boxes.
        boxes_b (np.ndarray): An array of shape '(M, 4)' representing M bounding boxes.

    Returns:
        (np.ndarray): A 2D array containing the IoU values for each i, j values
        of boxes_a and boxes_b, respectively.

    """

    def box_area(box: np.ndarray) -> np.ndarray:
        """
        Calculate the area of a bounding box.

        Args:
            box (np.ndarray): A 2D array where each row represents a bounding box
                in the format '[x_min, y_min, x_max, y_max]'.

        Returns:
            (np.ndarray): The area of the bounding box
        """
        area: np.ndarray = (box[2] - box[0]) * (box[3] - box[1])
        return area

    area_a = box_area(boxes_a.T)
    area_b = box_area(boxes_b.T)

    top_left = np.maximum(boxes_a[:, None, :2], boxes_b[:, :2])
    bottom_right = np.minimum(boxes_a[:, None, 2:], boxes_b[:, 2:])

    area_inter = np.prod(np.clip(bottom_right - top_left, a_min=0, a_max=None), 2)

    iou: np.ndarray = area_inter / (area_a[:, None] + area_b - area_inter)
    return iou


def non_max_suppression(predictions: np.ndarray, iou_threshold: float = 0.5) -> np.ndarray:
    """
    Implements the non-maximum suppression algorithm for removal of redundant
    bounding boxes. The goal of this method is to retain the most relevant
    bounding boxes for each object.

    Args:
        predictions (np.ndarray): Array containing the coordinates of the bounding
        box and the confidence and category in each case, in the form:
                '[x_min, y_min, x_max, y_max, confidence, category]'.
        iou_threshold (float): The IoU threshold above which a bounding box is
            considered redundant if it belongs to the same category. Defaults to '0.5'.

    Returns:
        np.ndarray: A boolean array where 'True' indicates that
            the corresponding bounding box is kept, and 'False' indicates
            it is suppressed.

    """
    rows, _ = predictions.shape

    sort_index = np.flip(predictions[:, 4].argsort())
    predictions = predictions[sort_index]

    boxes = predictions[:, :4]
    categories = predictions[:, 5]
    ious = bbox_iou_batch(boxes, boxes) - np.eye(rows)

    keep = np.ones(rows, dtype=bool)

    for index, (iou, category) in enumerate(zip(ious, categories)):
        if not keep[index]:
            continue

        condition = (iou > iou_threshold) & (categories == category)
        keep = keep & ~condition

    out: np.ndarray = keep[sort_index.argsort()]
    return out
