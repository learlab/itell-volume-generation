import io
import json
import os
from typing import Any, Optional

import fitz
from PIL import Image
from pydantic import BaseModel


class BBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class Size(BaseModel):
    width_pct: str
    height_pct: str
    pixels: str


class NearbyText(BaseModel):
    above: list[str] = []
    below: list[str] = []
    left: list[str] = []
    right: list[str] = []


class ImageMetadata(BaseModel):
    filepath: str
    filename: str
    page_num: int
    image_id: str
    position: str
    bbox: BBox
    size: Size
    caption: Optional[str] = None
    nearby_text: NearbyText


class ExtractImages:
    """Utility to extract images and nearby metadata from a PDF.

    Attributes:
        pdf_path: Path to the PDF file.
        output_dir: Directory where extracted images and metadata are saved.
        metadata: List of metadata dictionaries for each extracted image.
    """

    def __init__(self, pdf_path: str, output_dir: str) -> None:
        """Initialize the extractor.

        Args:
            pdf_path: Path to the input PDF file.
            output_dir: Directory to write extracted images and metadata.
        """
        self.pdf_path: str = pdf_path
        self.output_dir: str = output_dir
        self.metadata: list[ImageMetadata] = []
        os.makedirs(self.output_dir, exist_ok=True)

    def describe_position(
        self,
        bbox: fitz.Rect,
        page_width: float,
        page_height: float,
    ) -> str:
        """Return a human-readable position description for an image bbox.

        Args:
            bbox: Tuple of (x0, y0, x1, y1) coordinates for the image on the page.
            page_width: Width of the page in the same units as bbox.
            page_height: Height of the page in the same units as bbox.

        Returns:
            A string describing vertical and horizontal position (e.g. "top-left").
        """
        x0, y0, x1, y1 = bbox
        x_center = (x0 + x1) / 2
        y_center = (y0 + y1) / 2
        width = x1 - x0

        h_pos = (
            "full-width"
            if width > page_width * 0.85
            else (
                "left"
                if x_center < page_width * 0.3
                else "center" if x_center < page_width * 0.7 else "right"
            )
        )
        v_pos = (
            "top"
            if y_center < page_height * 0.25
            else "middle" if y_center < page_height * 0.75 else "bottom"
        )

        return f"{v_pos} {h_pos}" if h_pos == "full-width" else f"{v_pos}-{h_pos}"

    def get_nearby_text(
        self,
        page: fitz.Page,
        img_bbox: tuple[float, float, float, float],
        distance: int = 50,
    ) -> NearbyText:
        """Find nearby text blocks around an image bbox.

        Args:
            page: A `fitz.Page` instance to search for text blocks.
            img_bbox: Tuple (x0, y0, x1, y1) for the image bounding box.
            distance: Padding distance (in page units) around the image to search.

        Returns:
            A dict with keys 'above', 'below', 'left', 'right' mapping to lists of strings.
        """
        x0, y0, x1, y1 = img_bbox
        search_bbox = (
            max(0, x0 - distance),
            max(0, y0 - distance),
            x1 + distance,
            y1 + distance,
        )
        text_blocks = page.get_text("blocks", clip=search_bbox)

        nearby_text = NearbyText()

        for block in text_blocks:
            if len(block) < 5:
                continue
            bx0, by0, bx1, by1, text = block[:5]
            bx0, by0, bx1, by1 = float(bx0), float(by0), float(bx1), float(by1)
            text = text.strip()
            if not text:
                continue

            if by1 < y0:
                nearby_text.above.append(text)
            elif by0 > y1:
                nearby_text.below.append(text)
            elif bx1 < x0:
                nearby_text.left.append(text)
            elif bx0 > x1:
                nearby_text.right.append(text)

        return nearby_text

    def find_caption(self, nearby_text: NearbyText) -> Optional[str]:
        """Try to heuristically identify a caption from nearby text.

        Prefers text below the image, then above. Uses simple heuristics to
        filter by length and the presence of common caption indicators.

        Args:
            nearby_text: The dictionary returned by `get_nearby_text`.

        Returns:
            The caption string if found, otherwise `None`.
        """
        for position in ["below", "above"]:
            texts = getattr(nearby_text, position)
            if texts:
                text = texts[0]
                if len(text) < 200 and (
                    any(
                        indicator in text.lower()
                        for indicator in [
                            "figure",
                            "fig.",
                            "image",
                            "photo",
                            "source:",
                            "credit:",
                        ]
                    )
                    or len(text.split()) < 30
                ):
                    return text
        return None

    def extract_img(self) -> list[dict[str, Any]]:
        """Extract images from the PDF and collect metadata.

        Scans each page for images, writes image files to `output_dir`, and
        gathers metadata including position, size and nearby text.

        Returns:
            A list of `ImageMetadata` instances for each extracted image.
        """
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError("PDF File not found")

        with fitz.open(self.pdf_path) as doc:
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)

                print(f"Page {page_num + 1}: {len(image_list)} image(s)")

                for image_index, img in enumerate(image_list, start=1):
                    base_image = doc.extract_image(img[0])
                    filename = (
                        f"page_{page_num + 1}_img_{image_index}.{base_image['ext']}"
                    )
                    filepath = os.path.join(self.output_dir, filename)

                    with open(filepath, "wb") as f:
                        f.write(base_image["image"])

                    bbox = page.get_image_bbox(img)
                    if not isinstance(bbox, fitz.Rect):
                        print(
                            "  Warning: Could not get bbox for image, skipping metadata."
                        )
                        continue
                    x0, y0, x1, y1 = bbox.x0, bbox.y0, bbox.x1, bbox.y1
                    image = Image.open(io.BytesIO(base_image["image"]))

                    nearby_text = self.get_nearby_text(page, bbox, distance=50)
                    width_pct = ((x1 - x0) / page.rect.width) * 100
                    height_pct = ((y1 - y0) / page.rect.height) * 100

                    self.metadata.append(
                        ImageMetadata(
                            filepath=filepath,
                            filename=filename,
                            page_num=page_num + 1,
                            image_id=f"image_page_{page_num + 1}_{image_index}",
                            position=self.describe_position(
                                bbox, page.rect.width, page.rect.height
                            ),
                            bbox=BBox(x0=x0, y0=y0, x1=x1, y1=y1),
                            size=Size(
                                width_pct=f"{width_pct:.1f}%",
                                height_pct=f"{height_pct:.1f}%",
                                pixels=f"{image.width}x{image.height}",
                            ),
                            caption=self.find_caption(nearby_text),
                            nearby_text=nearby_text,
                        )
                    )

        return [m.model_dump() for m in self.metadata]

    def save_metadata(self, output_path: str) -> None:
        """Write the collected metadata to a JSON file.

        Args:
            output_path: File path where JSON metadata will be written.
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([m.model_dump() for m in self.metadata], f, indent=2)
