# -*- coding: utf-8 -*-

from enum import Enum
from typing import Any

import cv2
import numpy as np
from pycocotools import mask as mask_util
from sinapsis_core.data_containers.annotations import ImageAnnotations, Segmentation
from sinapsis_core.data_containers.data_packet import ImagePacket
from sinapsis_core.utils.logging_utils import sinapsis_logger
from sinapsis_data_readers.helpers.coco_dataclasses import (
    CocoAnnotationsKeys,
    CocoJsonKeys,
)

from sinapsis_data_writers.templates.annotation_writers.base_annotation_writer import (
    FORMATTED_ANNOTATIONS,
    BaseAnnotationWriter,
)


class SegmentationFormat(str, Enum):
    """
    Enum for segmentation formats.
    RLE: Key for rle annotations
    POLYGON: Key for Polygon annotations
    """

    RLE = "rle"
    POLYGON = "polygon"


class COCOAnnotationWriter(BaseAnnotationWriter):
    """
    Template to store annotations in COCO format in a file in the local environment
    The template checks for the ImageAnnotations field in ImagePacket and extracts
    those corresponding to BBoxes, keypoints, and Segmentation masks. If needed,
    these annotations are converted to COCO format before being saved in the file

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: COCOAnnotationWriter
      class_name: COCOAnnotationWriter
      template_input: InputTemplate
      attributes:
        root_dir: $SINAPSIS_CACHE_DIR
        save_dir: '/path/to/desired/destination'
        output_file: annotations
        extension: json
        category_mapping: {}
        segmentation_format:
        - rle
        visibility_threshold: 0
        contour_threshold: 4

    """

    class AttributesBaseModel(BaseAnnotationWriter.AttributesBaseModel):
        """Attributes for the COCO Annotation Writer:

        Args:
        category_mapping (dict[str, int]):
            Mapping between category labels and their corresponding category IDs. This is required.
        segmentation_format (str):
            Format to save the segmentation ('polygon' or 'rle'). Defaults to 'rle'.
        visibility_threshold (int):
            Threshold value to determine the visibility of keypoints.
        contour_threshold (int):
            Minimum number of points in a contour to be considered valid.Defaults to 4.
        """

        category_mapping: dict[str, int]
        segmentation_format: SegmentationFormat = SegmentationFormat.RLE
        visibility_threshold: int = 0
        contour_threshold: int = 4

    @staticmethod
    def _get_bbox(annotation: ImageAnnotations) -> list[float]:
        """Extracts the bounding box from the annotation.

        Args:
            annotation (ImageAnnotations): The annotation object
            containing the bounding box.

        Returns:
            list[float]: A list representing the bounding box in
            [x, y, width, height] format.

        Raises:
            ValueError: If the bounding box is missing in the annotation.
        """
        if not annotation.bbox:
            sinapsis_logger.warning("No bounding boxes in ImageAnnotations")
            return []

        return [
            annotation.bbox.x,
            annotation.bbox.y,
            annotation.bbox.w,
            annotation.bbox.h,
        ]

    @staticmethod
    def _get_oriented_bbox(annotation: ImageAnnotations) -> list[float]:
        """Extracts the oriented bounding box from the annotation.

        Args:
            annotation (ImageAnnotations): The annotation object containing
            the oriented bounding box.

        Returns:
            list[float]|None: Optionally, a list representing the oriented
            bounding box or None if not available.
        """
        if annotation.oriented_bbox:
            return [
                annotation.oriented_bbox.x1,
                annotation.oriented_bbox.y1,
                annotation.oriented_bbox.x2,
                annotation.oriented_bbox.y2,
                annotation.oriented_bbox.x3,
                annotation.oriented_bbox.y3,
                annotation.oriented_bbox.x4,
                annotation.oriented_bbox.y4,
            ]
        return []

    def _get_keypoints(self, annotation: ImageAnnotations) -> tuple[list[float], int]:
        """Extracts keypoints from the annotation and counts valid keypoints.

        Args:
            annotation (Annotations): The annotation object containing keypoints.

        Returns:
            tuple[List[float], int]: A tuple containing a list of keypoints
            in [x, y, visibility] format and the number of visible keypoints.
        """
        if not annotation.keypoints:
            return [], 0

        keypoints = []
        num_keypoints = 0
        for kp in annotation.keypoints:
            x = max(round(kp.x, 3), 0)
            y = max(round(kp.y, 3), 0)
            visibility = 2 if (kp.score and kp.score > self.attributes.visibility_threshold) else 0
            keypoints.extend([x, y, visibility])
            if visibility > 0:
                num_keypoints += 1

        return keypoints, num_keypoints

    def _convert_segmentation_to_desired_format(self, segmentation: Segmentation) -> list | dict:
        """Converts segmentation input to the desired format (polygon or RLE).

        Args:
            segmentation (Segmentation): The segmentation object containing polygon or mask data.
        """
        if self.attributes.segmentation_format == SegmentationFormat.POLYGON:
            if segmentation.polygon is not None:
                return segmentation.polygon
            if segmentation.mask is not None:
                contours, _ = cv2.findContours(
                    segmentation.mask.astype(np.uint8),
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE,
                )
                return [
                    contour.flatten().tolist()
                    for contour in contours
                    if len(contour) >= self.attributes.contour_threshold
                ]
        elif self.attributes.segmentation_format == SegmentationFormat.RLE:
            if segmentation.mask is not None:
                encoded_rle = mask_util.encode(np.asfortranarray(segmentation.mask.astype(np.uint8)))
                if isinstance(encoded_rle["counts"], bytes):
                    encoded_rle["counts"] = encoded_rle["counts"].decode("utf-8")
                return encoded_rle
        return []

    def _get_segmentation(self, annotation: ImageAnnotations) -> list | dict:
        """Returns the segmentation based on the defined format.

        Args:
            annotation (Annotations): The annotation object containing segmentation data.
        """
        if annotation.segmentation:
            return self._convert_segmentation_to_desired_format(annotation.segmentation)
        return []

    def _get_category_id(self, label_str: str) -> int | None:
        """Converts label_str to category_id, assigning -1 for unknowns.

        Args:
            label_str (str): The label string to be converted to category ID.
        """
        if label_str.isdigit():
            self.logger.debug(
                "Label string '%s' is numeric. Defaulting to generic category.",
                label_str,
            )
            return -1
        category_id = self.attributes.category_mapping.get(label_str, -1)
        if category_id == -1:
            self.logger.debug("Label string '%s' not found in category mapping. Defaulting to generic category.")
        return category_id if category_id != -1 else None

    def _convert_annotation(self, idx: int, annotation: ImageAnnotations, image_packet: ImagePacket) -> dict:
        """Converts an annotation into the COCO format.

        Args:
            idx: Index of the annotation.
            annotation: The annotation object containing relevant data.
            image_packet: The ImagePacket object containing image metadata.

        Returns:
            dict: The converted annotation in COCO format with an optional oriented_bbox key.
        """
        bbox = self._get_bbox(annotation)
        oriented_bbox = self._get_oriented_bbox(annotation)
        keypoints, num_keypoints = self._get_keypoints(annotation)
        segmentation = self._get_segmentation(annotation)
        category_id = self._get_category_id(annotation.label_str or "")

        # Constructing the COCO annotation directly
        coco_annotation = {
            CocoAnnotationsKeys.ANNOTATION_ID: idx + 1,
            CocoAnnotationsKeys.IMAGE_ID: str(image_packet.id),
            CocoAnnotationsKeys.BBOX: bbox,
            CocoAnnotationsKeys.ORIENTED_BBOX: oriented_bbox,
            CocoAnnotationsKeys.SEGMENTATIONS: segmentation,
            CocoAnnotationsKeys.AREA: (max(0.0, annotation.area) if annotation.area else max(0.0, bbox[2] * bbox[3])),
            CocoAnnotationsKeys.IS_CROWD: (annotation.is_crowd if annotation.is_crowd is not None else 0),
            CocoAnnotationsKeys.KEYPOINTS: keypoints,
            CocoAnnotationsKeys.NUM_KEYPOINTS: num_keypoints,
            CocoAnnotationsKeys.CATEGORY_ID: (category_id if category_id is not None else -1),
        }

        return coco_annotation

    def _annotations_to_format(self, image_packet: ImagePacket) -> FORMATTED_ANNOTATIONS:
        """Converts image annotations to COCO format."""
        return [
            self._convert_annotation(idx, annotation, image_packet)
            for idx, annotation in enumerate(image_packet.annotations)
            if annotation.bbox
        ]

    def _get_category_definitions(self) -> list[dict]:
        """Creates category definitions or COCO format."""
        categories = [
            {
                CocoAnnotationsKeys.ANNOTATION_ID: category_id,
                "name": label_str,
                "supercategory": "object",
            }
            for label_str, category_id in self.attributes.category_mapping.items()
        ]
        if any(
            annotation[CocoAnnotationsKeys.CATEGORY_ID] == -1
            for folder_data in self.folder_annotations.values()
            for annotation in folder_data[CocoJsonKeys.ANNOTATIONS]
        ):
            categories.append(
                {
                    CocoAnnotationsKeys.ANNOTATION_ID: -1,
                    "name": "generic",
                    "supercategory": "object",
                }
            )
        return categories

    def save_annotations(self, all_annotations: dict[str, Any], folder_name: str) -> None:
        """
        Saves annotations including category definitions.
        
        Args:
            all_annotations (dict[str, Any]): full dictionary of
                annotations to be saved in the file
            folder_name (str): name of the folder where annotations are saved.
        """
        all_annotations["categories"] = self._get_category_definitions()
        super().save_annotations(all_annotations, folder_name)
