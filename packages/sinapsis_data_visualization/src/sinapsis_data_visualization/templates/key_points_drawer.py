# -*- coding: utf-8 -*-

import cv2
import numpy as np
from sinapsis_core.data_containers.annotations import ImageAnnotations, KeyPoint
from sinapsis_data_visualization.helpers.annotation_drawer_types import (
    KeyPointAppearance,
)
from sinapsis_data_visualization.helpers.color_utils import RGB_TYPE
from sinapsis_data_visualization.templates.bbox_drawer import BBoxDrawer


class KeyPointsDrawer(BBoxDrawer):
    """
    A class for drawing keypoints and oriented bounding boxes on images,
    extending from BBoxDrawer.

    This class allows the addition of keypoints as annotations on images,
    along with oriented bounding boxes.
    It inherits from the 'BBoxDrawer' class to reuse the functionality
    for drawing oriented bounding boxes and extends it to handle the
    drawing of keypoints, which can be visualized with customizable
    appearance properties.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: KeyPointsDrawer
      class_name: KeyPointsDrawer
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
        Appends the method to draw the keypoints on the image, to
        the drawing_strategies list.
        """
        self.drawing_strategies.append(self.draw_key_points_strategy)

    @staticmethod
    def draw_key_points(
        image: np.ndarray,
        key_points: list[KeyPoint],
        appearance: KeyPointAppearance,
    ) -> np.ndarray:
        """
        Draws keypoints from annotations on the given image.

        Args:
            image (np.ndarray): The image in which to draw the keypoints.
            key_points (List[KeyPoint]): A list of keypoints to be drawn
            on the image.
            appearance (KeyPointAppearance): Defines the visual properties
            (e.g., radius, color, thickness) of the keypoints.

        Returns:
            np.ndarray: The edited image with the keypoints drawn.
        """
        image = np.array(image, dtype="uint8")

        for kpt in key_points:
            cv2.circle(
                image,
                center=(int(kpt.x), int(kpt.y)),
                radius=appearance.radius,
                color=appearance.color,
                thickness=appearance.thickness,
                lineType=8,
                shift=0,
            )
        return image

    def draw_key_points_strategy(
        self,
        image: np.ndarray,
        annotation: ImageAnnotations,
        ann_color: RGB_TYPE,
    ) -> np.ndarray:
        """
        Strategy method to draw keypoints as part of the annotation process.

        This method is used in the drawing strategy pipeline to draw keypoints
        for a given annotation on the image.
        If keypoints are present in the annotation, they will be drawn on the
        image with the specified appearance properties.

        Args:
            image (np.ndarray): The image on which to draw the keypoints.
            annotation (ImageAnnotations): The annotation containing the keypoints.
            ann_color (RGB_TYPE): The color to use for drawing the keypoints.

        Returns:
            np.ndarray: The image with the keypoints drawn.
        """

        if annotation.keypoints:
            image = self.draw_key_points(
                image=image,
                key_points=annotation.keypoints,
                appearance=KeyPointAppearance(color=ann_color),
            )

        return image
