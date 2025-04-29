# -*- coding: utf-8 -*-

import json
import os
from abc import abstractmethod
from typing import Any, cast

import numpy as np
from pycocotools import mask
from sinapsis_core.data_containers.annotations import (
    BoundingBox,
    ImageAnnotations,
    KeyPoint,
    OrientedBoundingBox,
    Segmentation,
)
from sinapsis_core.data_containers.data_packet import ImagePacket
from sinapsis_core.template_base.base_models import TemplateAttributeType

from sinapsis_data_readers.helpers.coco_dataclasses import (
    CocoAnnotationsKeys,
    CocoJsonKeys,
)
from sinapsis_data_readers.templates.base_file_data_loader import (
    base_attributes_documentation,
)
from sinapsis_data_readers.templates.image_readers.image_folder_reader_cv2 import (
    FolderImageDatasetCV2,
)


class CocoImageDatasetBaseCV2(FolderImageDatasetCV2):
    """Base Class for Coco datasets using OpenCV library
    The template reads the annotations from a file path and reads the images from
    a certain location in the local environment.
    The BaseTemplate adds only labels to the annotations field of ImagePacket
    """

    class AttributesBaseModel(FolderImageDatasetCV2.AttributesBaseModel):
        f""" Attributes for the datareader
        {base_attributes_documentation}
        annotations_path : str = path to the Coco annotations file
        """
        annotations_path: str

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        self.annotations_file = os.path.join(self.attributes.data_dir, self.attributes.annotations_path)
        self.raw_annotations_dict: list[dict[str, dict[str, Any]]] = self.read_annotations_file(self.annotations_file)
        self.annotations = self.images_annotations()

    @staticmethod
    def read_annotations_file(file: str) -> list[dict[str, dict[str, Any]]]:
        """Method to read the annotations file using json.

        Args:
            file (str): file with the annotations in json format

        Returns:
            list[dict[str, dict[str, Any]]]: The dictionary with the annotations
        """
        with open(file, encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
        f.close()
        anns_dict: list[dict[str, dict[str, Any]]] = data.get(CocoJsonKeys.ANNOTATIONS, [])
        return anns_dict

    @abstractmethod
    def get_annotations(self, image_annotations: list[dict[str, Any]]) -> list[ImageAnnotations]:
        """Abstract method to get annotations depending on the task.

        Args:
            image_annotations (list[dict[str, Any]]): List of annotation dictionaries.

        Returns:
            list[ImageAnnotations]: List of ImageAnnotations objects with label and bboxes.
        """

    def images_annotations(self) -> dict[str, list[dict[str, Any]]]:
        """Returns all the image annotations for all the images in the annotations file.

        Returns:
            dict[str, list[dict[str, Any]]]: Dictionary with keys being the id of the image
            and values being the list of annotations of the specific image.
        """
        annotation: dict[str, list[dict[str, Any]]] = {}
        for _, coco_annotation in enumerate(self.raw_annotations_dict):
            coco_annotation = cast(dict, coco_annotation)
            image_id: str = str(coco_annotation[CocoAnnotationsKeys.IMAGE_ID])
            if image_id not in annotation:
                annotation[image_id] = []

            annotation[image_id].append(coco_annotation)
        return annotation

    def read_packet_content(self, data_packet: ImagePacket) -> None:
        """Processes the content of the image and adds the
        ImageAnnotations objects to the ImagePacket

        Args:
            data_packet (ImagePacket): Packet to read the content
            from and to add the annotations

        """
        super().read_packet_content(data_packet)
        height, width, _ = data_packet.content.shape
        image_id = str(int(data_packet.annotations[0].label_str.split(".")[0]))

        annotations: list[ImageAnnotations] = self.get_annotations(self.annotations.get(image_id, []))
        data_packet.annotations = self._handle_masks(annotations, height, width)

    def _handle_masks(self, annotations: list[ImageAnnotations], height: int, width: int) -> list[ImageAnnotations]:
        """Handles masks for annotations.

        Args:
            annotations (List[ImageAnnotations]): List of annotations.
            height (int): Image height.
            width (int): Image width.

        Returns:
            List[ImageAnnotations]: The list of annotations with masks handled.
        """
        _, _ = height, width
        return annotations


class CocoDetectionDatasetCV2(CocoImageDatasetBaseCV2):
    """Specific template for Coco Detection datasets
    This template reads the annotations for BoundingBoxes and Oriented BoundingBoxes
    and adds them to the ImagePackets

    Usage example:

        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: CocoDetectionDatasetCV2
          class_name: CocoDetectionDatasetCV2
          template_input: InputTemplate
          attributes:
            data_dir: '/path/to/data/dir'
            pattern: '**/*'
            batch_size: 1
            shuffle_data: false
            samples_to_load: -1
            load_on_init: false
            label_path_index: -2
            is_ground_truth: false
            annotations_path: '/path/to/annotations/file.json'

    """

    def get_annotations(self, image_annotations: list[dict[str, Any]]) -> list[ImageAnnotations]:
        """Converts COCO annotations to ImageAnnotations objects.

        Args:
            image_annotations (list[dict[str, Any]]): COCO annotations for an image.

        Returns:
            list[ImageAnnotations]: List of ImageAnnotations for the image with bboxes and oriented bboxes.
        """
        list_of_annotations: list[ImageAnnotations] = []
        if image_annotations:
            for annotation in image_annotations:
                this_ann_bbox = BoundingBox(
                    x=annotation[CocoAnnotationsKeys.BBOX][0],
                    y=annotation[CocoAnnotationsKeys.BBOX][1],
                    w=annotation[CocoAnnotationsKeys.BBOX][2],
                    h=annotation[CocoAnnotationsKeys.BBOX][3],
                )
                label_ann = annotation[CocoAnnotationsKeys.CATEGORY_ID]

                oriented_bbox_data = annotation.get(CocoAnnotationsKeys.ORIENTED_BBOX, None)
                oriented_bbox = None
                if oriented_bbox_data:
                    oriented_bbox = OrientedBoundingBox(
                        x1=oriented_bbox_data[0],
                        y1=oriented_bbox_data[1],
                        x2=oriented_bbox_data[2],
                        y2=oriented_bbox_data[3],
                        x3=oriented_bbox_data[4],
                        y3=oriented_bbox_data[5],
                        x4=oriented_bbox_data[6],
                        y4=oriented_bbox_data[7],
                    )

                list_of_annotations.append(
                    ImageAnnotations(
                        label=label_ann,
                        label_str=str(label_ann),
                        bbox=this_ann_bbox,
                        oriented_bbox=oriented_bbox,
                        is_ground_truth=self.attributes.is_ground_truth,
                        is_crowd=annotation[CocoAnnotationsKeys.IS_CROWD],
                        area=annotation[CocoAnnotationsKeys.AREA],
                    )
                )
        return list_of_annotations


class CocoSegmentationDatasetCV2(CocoDetectionDatasetCV2):
    """Specific template for Coco Segmentation datasets
    This template reads the annotations for BoundingBoxes,
    Oriented BoundingBoxes and Segmentation masks
    and adds them to the ImagePackets.

    Usage example:

        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: CocoSegmentationDatasetCV2
          class_name: CocoSegmentationDatasetCV2
          template_input: InputTemplate
          attributes:
            data_dir: '/path/to/data/dir'
            pattern: '**/*'
            batch_size: 1
            shuffle_data: false
            samples_to_load: -1
            load_on_init: false
            label_path_index: -2
            is_ground_truth: false
            annotations_path: '/path/to/annotations/file.json'
    """

    def get_annotations(self, image_annotations: list[dict[str, Any]]) -> list[ImageAnnotations]:
        """Process the segmentation annotations and append to the ImageAnnotations object for ImagePackets
        Args:
            image_annotations (list[dict[str, Any]]): ImageAnnotations dictionary for individual image
        Returns:
           list[ImageAnnotations]: Update list of ImageAnnotations with segmentation objects.
        """
        annotations = super().get_annotations(image_annotations)

        if image_annotations:
            for i, ann in enumerate(image_annotations):
                coco_segmentation = ann.get(CocoAnnotationsKeys.SEGMENTATIONS, None)
                segmentation = None
                if coco_segmentation is not None:
                    if isinstance(coco_segmentation, list):
                        segmentation = Segmentation(polygon=coco_segmentation)
                    elif isinstance(coco_segmentation, dict):
                        segmentation = Segmentation(rle=coco_segmentation)
                annotations[i].segmentation = segmentation
        return annotations

    @staticmethod
    def get_binary_mask(
        mask_coords: dict[Any, Any] | list[list[float]],
        height: int,
        width: int,
        cat_id: int,
    ) -> np.ndarray:
        """Defines the binary mask for the image based on the coordinates.

        Args:
            mask_coords (Union[Dict, List[List[float]]]): Coordinates of the mask.
            height (int): Image height.
            width (int): Image width.
            cat_id (int): Category ID of the object.

        Returns:
            np.ndarray: Binary mask of the object.
        """

        if isinstance(mask_coords, list):
            rles = mask.frPyObjects(mask_coords, height, width)
            rle = mask.merge(rles)
        elif isinstance(mask_coords, dict) and "counts" in mask_coords:
            rle = mask_coords
            if isinstance(rle["counts"], list):
                rle = mask.frPyObjects([rle], height, width)[0]
        else:
            raise ValueError("Unsupported mask format or invalid RLE data.")

        binary_mask: np.ndarray = mask.decode(rle).astype(np.uint8)
        return binary_mask * cat_id

    def _handle_masks(self, annotations: list[ImageAnnotations], height: int, width: int) -> list[ImageAnnotations]:
        """Processes and applies masks to annotations.

        Args:
            annotations (List[ImageAnnotations]): List of annotations.
            height (int): Image height.
            width (int): Image width.

        Returns:
            List[ImageAnnotations]: ImageAnnotations with masks applied.
        """
        for ann in annotations:
            if ann.segmentation:
                if ann.segmentation.polygon:
                    ann.segmentation.mask = self.get_binary_mask(ann.segmentation.polygon, height, width, ann.label)
                elif ann.segmentation.rle:
                    ann.segmentation.mask = self.get_binary_mask(ann.segmentation.rle, height, width, ann.label)
                ann.segmentation.polygon = None
                ann.segmentation.rle = None

        return annotations


class CocoKeypointsDatasetCV2(CocoDetectionDatasetCV2):
    """Specific template for Coco Keypoints datasets
    This template reads the annotations for BoundingBoxes,
    Oriented BoundingBoxes and Keypoints
    and adds them to the ImagePackets

    Usage example:

        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: CocoKeypointsDatasetCV2
          class_name: CocoKeypointsDatasetCV2
          template_input: InputTemplate
          attributes:
            data_dir: '/path/to/data/dir'
            pattern: '**/*'
            batch_size: 1
            shuffle_data: false
            samples_to_load: -1
            load_on_init: false
            label_path_index: -2
            is_ground_truth: false
            annotations_path: '/path/to/annotations/file.json'
    """

    def get_annotations(self, image_annotations: list[dict[str, Any]]) -> list[ImageAnnotations]:
        annotations = super().get_annotations(image_annotations)
        if image_annotations:
            for j, ann in enumerate(image_annotations):
                keypoints_data = ann.get(CocoAnnotationsKeys.KEYPOINTS, None)
                keypoints_list = []
                if keypoints_data:
                    num_keypoints = ann.get(CocoAnnotationsKeys.NUM_KEYPOINTS, len(keypoints_data) // 3)
                    for i in range(num_keypoints):
                        x = keypoints_data[i * 3]
                        y = keypoints_data[i * 3 + 1]
                        visibility = keypoints_data[i * 3 + 2]
                        score = ann.get(CocoAnnotationsKeys.SCORE, None)
                        keypoints_list.append(KeyPoint(x=x, y=y, visibility=visibility, score=score))
                    annotations[j].keypoints = keypoints_list
                    annotations[j].n_keypoints = len(keypoints_list)
        return annotations
