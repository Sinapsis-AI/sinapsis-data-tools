# -*- coding: utf-8 -*-


import cv2
import numpy as np
from sinapsis_core.data_containers.annotations import (
    ImageAnnotations,
    OrientedBoundingBox,
)
from sinapsis_data_visualization.helpers.color_utils import RGB_TYPE
from sinapsis_data_visualization.templates.bbox_drawer import BBoxDrawer


class OrientedBBoxDrawer(BBoxDrawer):
    """
    A class for drawing oriented bounding boxes on images,

    This class allows the addition of oriented bounding boxes
    along with the label annotations by implementing adding the method
    'draw_oriented_bbox' to the drawing_strategy


    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: OrientedBBoxDrawer
      class_name: OrientedBBoxDrawer
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
        Appends the method to draw the oriented bbox on the image, to
        the drawing_strategies list.
        """
        self.drawing_strategies.append(self.draw_oriented_bbox_strategy)

    @staticmethod
    def draw_oriented_bbox(
        image: np.ndarray,
        oriented_bbox: OrientedBoundingBox,
        color: RGB_TYPE,
        thickness: int = 2,
    ) -> np.ndarray:
        """
        Draws an oriented bounding box (polygon) on the image.

        Args:
            image (np.ndarray): The image to draw the oriented bounding box on.
            oriented_bbox (OrientedBoundingBox): The oriented bounding box
            to be drawn (containing 4 points).
            color (RGB_TYPE): The color of the bounding box in RGB format.
            thickness (int, optional): The thickness of the bounding box lines.

        Returns:
            np.ndarray: The image with the oriented bounding box drawn.
        """
        image = np.array(image, dtype="uint8")

        pts = np.array(
            [
                [int(oriented_bbox.x1), int(oriented_bbox.y1)],
                [int(oriented_bbox.x2), int(oriented_bbox.y2)],
                [int(oriented_bbox.x3), int(oriented_bbox.y3)],
                [int(oriented_bbox.x4), int(oriented_bbox.y4)],
            ]
        )
        cv2.polylines(img=image, pts=[pts], isClosed=True, color=color, thickness=thickness)

        return image

    def draw_oriented_bbox_strategy(
        self,
        image: np.ndarray,
        annotation: ImageAnnotations,
        ann_color: RGB_TYPE,
    ) -> np.ndarray:
        """
        Strategy method to draw both the oriented bounding box and any
        associated label annotations on the image.

        This method is used as part of the drawing strategy to draw an
        oriented bounding box and associated labels for the given annotation.

        Args:
            image (np.ndarray): The image to draw on.
            annotation (ImageAnnotations): The annotation containing the
            oriented bounding box and label data.
            ann_color (RGB_TYPE): The color to use for the bounding box and text.

        Returns:
            np.ndarray: The image with the oriented bounding box and labels drawn.
        """

        if annotation.oriented_bbox:
            image = self.draw_oriented_bbox(
                image=image,
                oriented_bbox=annotation.oriented_bbox,
                color=ann_color,
            )

        return image
