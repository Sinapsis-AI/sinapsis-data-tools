# -*- coding: utf-8 -*-

import cv2
import numpy as np
from sinapsis_core.data_containers.annotations import BoundingBox, ImageAnnotations
from sinapsis_data_visualization.helpers.color_utils import RGB_TYPE
from sinapsis_data_visualization.templates.label_drawer import LabelDrawer


class BBoxDrawer(LabelDrawer):
    """
    A class for drawing bounding boxes in images, extending from the LabelDrawer template.

    This class allows the addition of bounding boxes along with the label annotations
    by implementing a drawing strategy that draws both bounding boxes and associated labels.
    It inherits from the `LabelDrawer` class, leveraging its functionality for label drawing
    and customization.

    Usage example:
    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: BBoxDrawer
      class_name: BBoxDrawer
      template_input: InputTemplate
      attributes:
        overwrite: false
        randomized_color: true
        draw_confidence: true
        draw_extra_labels: true
        text_style:
          font: 0
          font_scale: 0.5
          thickness: 2
        draw_classification_label: false
        classification_label_position: top_right
        text_box_to_border_offset: 0.01


    """

    def set_drawing_strategy(self) -> None:
        """
        Appends the method to draw the bbox on the image, to
        the drawing_strategies list.
        """
        super().set_drawing_strategy()
        self.drawing_strategies.insert(0, self.draw_bbox_strategy)

    @staticmethod
    def draw_bbox(
        image: np.ndarray,
        bbox: BoundingBox,
        color: RGB_TYPE,
        thickness: int = 2,
    ) -> np.ndarray:
        """
        Draws a bounding box on the given image.

        Args:
            image (np.ndarray): The image to draw on.
            bbox (BoundingBox): The bounding box to be drawn on the image.
            color (RGB_TYPE): The color of the bounding box (in RGB format).
            thickness (int, optional): The thickness of the bounding box lines. Defaults to 2.

        Returns:
            np.ndarray: The image with the bounding box drawn.
        """
        image = np.array(image, dtype="uint8")
        cv2.rectangle(
            img=image,
            pt1=(int(bbox.x), int(bbox.y)),
            pt2=(int(bbox.x) + int(bbox.w), int(bbox.y) + int(bbox.h)),
            color=color,
            thickness=thickness,
        )
        return image

    def draw_bbox_strategy(self, image: np.ndarray, annotation: ImageAnnotations, ann_color: RGB_TYPE) -> np.ndarray:
        """
        Strategy method to draw both bounding boxes and labels on the image.

        This method is used as part of the drawing strategy to draw a bounding box and
        associated labels (if applicable) for the given annotation.

        Args:
            image (np.ndarray): The image to draw on.
            annotation (ImageAnnotations): The annotation containing the bounding box and label data.
            ann_color (RGB_TYPE): The color to use for the bounding box and text.

        Returns:
            np.ndarray: The image with the bounding box and label drawn.
        """
        if annotation.bbox:
            image = self.draw_bbox(
                image=image,
                bbox=annotation.bbox,
                color=ann_color,
            )

        return image
