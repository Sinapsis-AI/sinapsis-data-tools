# -*- coding: utf-8 -*-

from typing import Literal

import numpy as np
from sinapsis_core.data_containers.annotations import BoundingBox, ImageAnnotations
from sinapsis_data_visualization.helpers.annotation_drawer_tools import (
    draw_annotation_rectangle,
    draw_extra_labels,
    draw_text,
    get_dynamic_text_properties,
    get_extra_ann_labels,
    get_numeric_str,
    get_text_coordinates,
    get_text_size,
)
from sinapsis_data_visualization.helpers.annotation_drawer_types import (
    TextInstanceProperties,
    TextStyle,
)
from sinapsis_data_visualization.helpers.color_utils import (
    RGB_TYPE,
    darken_or_lighten_color,
)
from sinapsis_data_visualization.templates.base_annotation_drawer import (
    BaseAnnotationDrawer,
)


class LabelDrawer(BaseAnnotationDrawer):
    """
    Template to insert label annotations in images.

    The template inherits the functionality from the BaseAnnotationDrawer
    and allows to draw classification labels and labels associated with a
    given annotation.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: LabelDrawer
      class_name: LabelDrawer
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

    class AttributesBaseModel(BaseAnnotationDrawer.AttributesBaseModel):
        """
        Attributes for Label Annotation Drawer

        Args:
            draw_confidence (bool): Flag to determine confidence value is
                drawn. Defaults to True
            draw_extra_labels (bool): Flag to determine if extra labels are drawn.
                Defaults to True
            text_style (TextStyle) = {font=0, font_scale=0.5, thickness=2}:
                Dictionary of font properties used to draw label text boxes.
            draw_classification_label (bool): Flag to determine if a classification label
                is drawn on the image. Defaults to False.
            classification_label_position (str): Position of the text box for the
                classification label. Defaults to "top_right".
            text_box_to_border_offset (float): Weight to control offset of text box to image border.
        """

        draw_confidence: bool = True
        draw_extra_labels: bool = True
        text_style: TextStyle = TextStyle()
        draw_classification_label: bool = False
        classification_label_position: Literal["top_left", "top_right"] = "top_right"
        text_box_to_border_offset: float = 0.01

    def set_drawing_strategy(self) -> None:
        """Appends the annotation to be drawn (i.e., label)
        to the list of tasks in the execute method"""
        self.drawing_strategies.append(self.draw_label_strategy)

    def _parse_extra_labels(
        self,
        annotation: ImageAnnotations,
        annotation_str_repr: str,
        spacing: int = 5,
    ) -> tuple[list[int], list[str], int, int]:
        """
        Parses extra annotations (if any) to be drawn below the primary label.

        Args:
            annotation (ImageAnnotations): The annotation containing extra labels.
            annotation_str_repr (str): The string representation of the main annotation label.
            spacing (int, optional): Spacing between extra labels.

        Returns:
            tuple:
                - text_y_offsets (list[int]): Y offsets for each extra label.
                - extra_str_repr (list[str]): The string representations of extra labels.
                - text_w (int): The maximum width of the labels.
                - text_h (int): The height of all labels combined.
        """

        text_w, text_h = get_text_size(annotation_str_repr, self.attributes.text_style)
        text_y_offsets, extra_str_repr = [], []
        extra_text_h = text_h
        if self.attributes.draw_extra_labels and annotation.extra_labels is not None:
            text_y_offsets, extra_str_repr, extra_text_h, text_w = get_extra_ann_labels(
                annotation, text_w, text_h, self.attributes.text_style, spacing
            )

        return text_y_offsets, extra_str_repr, text_w, extra_text_h

    def get_label_ann_str(self, annotation: ImageAnnotations) -> str:
        """
        Returns the annotation as string, appending confidence score if needed.

        Args:
            annotation (ImageAnnotations): Annotation object in the ImagePacket to
            extract the label from

        """
        if not annotation.label_str:
            return ""
        annotation_str_repr = f"{annotation.label_str}"
        if self.attributes.draw_confidence and annotation.confidence_score:
            annotation_str_repr = get_numeric_str(annotation_str_repr, annotation.confidence_score)
        return annotation_str_repr

    def get_label_properties(
        self,
        shape: tuple,
        annotation: ImageAnnotations,
        class_label: bool = False,
        spacing: int = 5,
    ) -> tuple:
        """
        Calculates the label properties needed for to draw annotations on an image.

        Args:
            shape (tuple): The dimensions of the image as (height, width).
            annotation (ImageAnnotations): The annotation data containing
            the label and additional information.
            class_label (bool, optional): Specifies whether the label is
            for a classification. If 'True', the label is positioned
            globally within the image; otherwise, it is placed near the
            bounding box.

            spacing (int, optional): The spacing between the primary label
            and additional labels.

        Returns:
            tuple: A tuple containing:
                - 'BoundingBox': The bounding box for the label text.
                - 'str': The main annotation string representation.
                - 'list[str]': Additional label strings, if any.
                - 'list[int]': Vertical offsets for additional labels.
                - 'int': Width of the text bounding box.
                - 'int': Height of the text bounding box.
        """
        annotation_str_repr = self.get_label_ann_str(annotation)
        text_y_offsets, extra_str_repr, text_w, text_h = self._parse_extra_labels(
            annotation, annotation_str_repr, spacing
        )
        _, top_text_h = get_text_size(annotation_str_repr, self.attributes.text_style)
        text_coords = top_text_h, text_w
        if class_label:
            x, y = get_text_coordinates(
                shape,
                text_coords,
                self.attributes.text_box_to_border_offset,
                self.attributes.classification_label_position,
            )
            bbox = BoundingBox(x, y + text_h - top_text_h, text_w, text_h)
        else:
            bbox = annotation.bbox
        return bbox, annotation_str_repr, extra_str_repr, text_y_offsets, text_w, text_h

    def add_label(
        self,
        image_info: tuple[np.ndarray, ImageAnnotations, RGB_TYPE],
        spacing: int = 5,
        class_label: bool = False,
    ) -> np.ndarray:
        """
        Adds label to the image

        Args:
            image_info (tuple): Information of the image where
            annotation is to be Drawn: the actual image as an array,
            the annotation where label is stored and the color of the annotation.
            spacing (int): Space between different annotations if more than one
            class_label (bool): Flag to determine if the label is from classification.

        """
        image, annotation, ann_color = image_info
        h, w = image.shape[:2]

        bbox, annotation_str_repr, extra_str_labels, text_y_offset, text_w, text_h = self.get_label_properties(
            (h, w), annotation, class_label, spacing
        )
        text_color = darken_or_lighten_color(ann_color)
        image = draw_annotation_rectangle(image, bbox, ann_color, text_h, text_w)
        if extra_str_labels and text_y_offset:
            image = draw_extra_labels(
                image,
                annotation.bbox,
                extra_str_labels,
                text_y_offset,
                text_color,
                self.attributes.text_style,
            )

        image = draw_text(
            image,
            annotation_str_repr,
            TextInstanceProperties(
                bbox.x,
                bbox.y - self.attributes.text_style.font_scale,
                text_color,
            ),
            self.attributes.text_style,
        )
        return image

    def add_classification_label(
        self,
        image_info: tuple[np.ndarray, ImageAnnotations, RGB_TYPE],
        class_label: bool = False,
    ) -> np.ndarray:
        """
        Adds the classification label to the image

        Args:
            - image_info (tuple): information of the image containing
            the actual image to draw the annotation on, the annotation
            object and the annotation color.
            - class_label (bool): flag to determine if the label is a
            classification label, in which case, there is no bounding
            box associated with it. Adds a classification label annotation
            to the image

        Returns:
            np.ndarray: The image with the added classification label and associated bounding box.
        """

        image = image_info[0]
        font_scale, font_thickness = get_dynamic_text_properties(image)
        self.attributes.text_style.font_scale = font_scale
        self.attributes.text_style.thickness = font_thickness

        image = self.add_label(image_info=image_info, class_label=class_label, spacing=int(5 * font_scale))

        return image

    def draw_label_strategy(self, image: np.ndarray, annotation: ImageAnnotations, ann_color: RGB_TYPE) -> np.ndarray:
        """
        Strategy for drawing labels on the image, either classification
        or regular labels based on attributes.

        Args:
            image (np.ndarray): The image to draw on.
            annotation (ImageAnnotations): The annotation containing
                the label to be drawn.
            ann_color (RGB_TYPE): The color for the label.

        Returns:
            np.ndarray: The image with the label drawn, either classification or regular.
        """
        if not annotation.label_str and not annotation.confidence_score:
            return image

        if annotation.label_str and self.attributes.draw_classification_label:
            image = self.add_classification_label(image_info=(image, annotation, ann_color), class_label=True)
        if annotation.bbox:
            image = self.add_label(image_info=(image, annotation, ann_color))

        return image
