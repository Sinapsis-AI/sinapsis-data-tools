# -*- coding: utf-8 -*-

import numpy as np
from sinapsis_core.data_containers.annotations import ImageAnnotations, Segmentation
from sinapsis_data_visualization.helpers.color_utils import RGB_TYPE
from sinapsis_data_visualization.templates.bbox_drawer import BBoxDrawer


class SegmentationMaskDrawer(BBoxDrawer):
    """
    A class for drawing segmentation masks and keypoints on images,
    extending from BBoxDrawer.

    This class allows drawing segmentation masks (binary or RGB masks)
    along with keypoints on images.
    It inherits from the `BBoxDrawer` class to reuse its functionality
    for drawing bounding boxes and adds the ability to handle segmentation
    masks, which can be overlaid with specific transparency levels (alpha).

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: SegmentationMaskDrawer
      class_name: SegmentationMaskDrawer
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
        alpha: 0.5
    """

    class AttributesBaseModel(BBoxDrawer.AttributesBaseModel):
        """
        Nested class to define the specific attributes for segmentation mask drawing.

        The `alpha` attribute controls the transparency of the segmentation mask,
        where 0 is fully transparent and 1 is fully opaque.
        """

        alpha: float = 0.5

    def set_drawing_strategy(self) -> None:
        """
        Appends the method to draw the segmentation masks on the image, to
        the drawing_strategies list.
        """
        self.drawing_strategies.append(self.draw_segmentation_strategy)

    @staticmethod
    def draw_segmentation(
        image: np.ndarray,
        segmentation: Segmentation,
        color: RGB_TYPE,
        alpha: float,
    ) -> np.ndarray:
        """
        Draws a binary segmentation mask on the image with
        specified transparency (alpha).

        Args:
            image (np.ndarray): The image in which to draw the segmentation mask.
            segmentation (Segmentation): The binary segmentation mask
            (1 for object, 0 for background).
            color (RGB_TYPE): The color to use for the segmented object.
            alpha (float): Transparency of the mask. 0 is completely transparent,
            1 is completely opaque.

        Returns:
            np.ndarray: The edited image with the segmentation mask applied.
        """
        # If the image is grayscale, convert it to RGB:
        if image.ndim == 2:
            image = np.stack((image,) * 3, axis=-1)
        # Create an empty RGB mask:
        rgb_mask = np.zeros_like(image, dtype=np.float32)
        mask_condition = segmentation.mask == 1
        # Assign the color to the mask where the condition is True:
        rgb_mask[mask_condition] = color
        # Blend the image and the mask using alpha transparency:
        blended_img_np = np.zeros_like(image, dtype=np.float32)
        blended_img_np[mask_condition] = image[mask_condition] * (1.0 - alpha) + rgb_mask[mask_condition] * alpha
        # Keep the original image where the mask condition is False:
        blended_img_np[~mask_condition] = image[~mask_condition]
        # Convert the image back to uint8 for displaying:
        blended_img_np = blended_img_np.astype(np.uint8)
        return blended_img_np

    def draw_segmentation_strategy(
        self,
        image: np.ndarray,
        annotation: ImageAnnotations,
        ann_color: RGB_TYPE,
    ) -> np.ndarray:
        """
        Strategy method to draw the segmentation mask as part of the
        annotation process.

        This method is part of the drawing strategy pipeline, responsible
        for drawing a segmentation mask
        for a given annotation. If a segmentation mask is present in the
        annotation, it will be drawn
        with the specified color and transparency level.

        Args:
            image (np.ndarray): The image on which to draw the segmentation mask.
            annotation (ImageAnnotations): The annotation containing the
                segmentation mask.
            ann_color (RGB_TYPE): The color to use for drawing the segmentation mask.

        Returns:
            np.ndarray: The image with the segmentation mask drawn.
        """

        if annotation.segmentation is not None:
            image = self.draw_segmentation(
                image=image,
                segmentation=annotation.segmentation,
                color=ann_color,
                alpha=self.attributes.alpha,
            )

        return image
