# -*- coding: utf-8 -*-
from functools import cached_property
from typing import cast

import cv2
import numpy as np
from pydantic import BaseModel, ConfigDict, computed_field
from sinapsis_core.data_containers.annotations import ImageAnnotations, KeyPoint, Segmentation
from sinapsis_core.data_containers.data_packet import DataContainer
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import (
    OutputTypes,
    TemplateAttributes,
    UIPropertiesMetadata,
)

from sinapsis_generic_data_tools.helpers.tags import Tags


class RegionOfInterest(BaseModel):
    """BaseModel to store the region of interest"""

    roi: list[KeyPoint]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @computed_field
    @cached_property
    def as_numpy_array(self) -> np.ndarray:
        """Returns the roi as a numpy array"""
        coors = [[point.x, point.y] for point in self.roi]
        return np.array(coors, dtype=np.int32)


class MaskNonROIs(Template):
    """
    Template that assigns segmentation masks to non-regions of interest.
    The template assigns a zero to all the pixels not in the roi
    and returns an image where non-zero pixels correspond to the actual
    roi mask.

    Usage example:
    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: MaskNonROIs
      class_name: MaskNonROIs
      template_input: InputTemplate
      attributes:
        rois_to_keep:
            - roi:
            - x: 657
                y: 619
            - x: 1220
                y: 580
            - x: 1343
                y: 733
            - x: 682
                y: 789
            - roi:
                -x ....;
        return_in_generic: false
        return_as_mask: false

    """

    UIProperties = UIPropertiesMetadata(
        output_type=OutputTypes.IMAGE,
        tags=[Tags.SEGMENTATION, Tags.MASK, Tags.IMAGE, Tags.ROI],
    )

    class AttributesBaseModel(TemplateAttributes):
        """
        Example usage:
            rois_to_keep:
              - roi:
                - x: 657
                  y: 619
                - x: 1220
                  y: 580
                - x: 1343
                  y: 733
                - x: 682
                  y: 789
              - roi:
                 -x ....;
        """

        rois_to_keep: list[RegionOfInterest]
        return_in_generic: bool = False
        return_as_mask: bool = False

    attributes: AttributesBaseModel

    def mask_non_rois(self, image: np.ndarray, use_bitwise: bool = True) -> np.ndarray:
        """
        Removed non-region of interest areas in an image, keeping only
        the regions specified in the attributes.

        Args:
            image (np.ndarray): image to be masked
            use_bitwise (bool): Flag to indicate if using cv2.bitwise_and
            (True) or np.where (False).
        """
        masked_img = np.zeros_like(image, image.dtype)
        for roi in self.attributes.rois_to_keep:
            if not use_bitwise:
                cv2.fillPoly(masked_img, [roi.as_numpy_array], (1, 1, 1))
                masked_img = np.where(masked_img, image, 0)
            else:
                cv2.fillPoly(masked_img, [roi.as_numpy_array], (255, 255, 255))
                masked_img = cv2.bitwise_and(image, masked_img)

        return masked_img

    def execute(self, container: DataContainer) -> DataContainer:
        for image_packet in container.images:
            image = image_packet.content
            if self.attributes.return_as_mask:
                mask = np.zeros(image.shape[:2], dtype=np.uint8)
                for roi in self.attributes.rois_to_keep:
                    cv2.fillPoly(mask, [roi.as_numpy_array], (1, 1, 1))
                    image_packet.annotations.append(ImageAnnotations(segmentation=Segmentation(mask=mask)))
            else:
                masked_img = self.mask_non_rois(image)
                if self.attributes.return_in_generic:
                    image_packet.generic_data[cast(str, self.class_name)] = masked_img
                else:
                    image_packet.content = masked_img
        return container
