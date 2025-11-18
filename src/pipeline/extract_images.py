import fitz
import os
import json
from PIL import Image
import io


class ExtractImages:
    def __init__(self, pdf_path, output_dir):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.metadata = []
        os.makedirs(self.output_dir, exist_ok=True)

    def describe_position(self, bbox, page_width, page_height):
        x0, y0, x1, y1 = bbox
        x_center = (x0 + x1) / 2
        y_center = (y0 + y1) / 2
        width = x1 - x0

        h_pos = "full-width" if width > page_width * 0.85 else (
            "left" if x_center < page_width * 0.3 else
            "center" if x_center < page_width * 0.7 else "right"
        )
        v_pos = "top" if y_center < page_height * 0.25 else "middle" if y_center < page_height * 0.75 else "bottom"

        return f"{v_pos} {h_pos}" if h_pos == "full-width" else f"{v_pos}-{h_pos}"

    def get_nearby_text(self, page, img_bbox, distance=50):
        x0, y0, x1, y1 = img_bbox
        search_bbox = (max(0, x0 - distance), max(0, y0 - distance), x1 + distance, y1 + distance)
        text_blocks = page.get_text("blocks", clip=search_bbox)

        nearby_text = {'above': [], 'below': [], 'left': [], 'right': []}

        for block in text_blocks:
            if len(block) < 5:
                continue
            bx0, by0, bx1, by1, text, *_ = block
            text = text.strip()
            if not text:
                continue

            if by1 < y0:
                nearby_text['above'].append(text)
            elif by0 > y1:
                nearby_text['below'].append(text)
            elif bx1 < x0:
                nearby_text['left'].append(text)
            elif bx0 > x1:
                nearby_text['right'].append(text)

        return nearby_text

    def find_caption(self, nearby_text):
        for position in ['below', 'above']:
            if nearby_text[position]:
                text = nearby_text[position][0]
                if len(text) < 200 and (
                    any(ind in text.lower() for ind in ['figure', 'fig.', 'image', 'photo', 'source:', 'credit:'])
                    or len(text.split()) < 30
                ):
                    return text
        return None

    def extract_img(self, pdf_path):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF File not found")

        doc = fitz.open(pdf_path)

        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)

            print(f"Page {page_num + 1}: {len(image_list)} image(s)")

            for image_index, img in enumerate(image_list, start=1):
                base_image = doc.extract_image(img[0])
                filename = f"page_{page_num + 1}_img_{image_index}.{base_image['ext']}"
                filepath = os.path.join(self.output_dir, filename)

                with open(filepath, "wb") as f:
                    f.write(base_image["image"])

                bbox = page.get_image_bbox(img)
                x0, y0, x1, y1 = bbox
                image = Image.open(io.BytesIO(base_image["image"]))

                nearby_text = self.get_nearby_text(page, bbox, distance=50)
                width_pct = ((x1 - x0) / page.rect.width) * 100
                height_pct = ((y1 - y0) / page.rect.height) * 100

                self.metadata.append({
                    "filepath": filepath,
                    "filename": filename,
                    "page_num": page_num + 1,
                    "image_id": f"image_page_{page_num + 1}_{image_index}",
                    "position": self.describe_position(bbox, page.rect.width, page.rect.height),
                    "bbox": {"x0": x0, "y0": y0, "x1": x1, "y1": y1},
                    "size": {
                        "width_pct": f"{width_pct:.1f}%",
                        "height_pct": f"{height_pct:.1f}%",
                        "pixels": f"{image.width}x{image.height}"
                    },
                    "caption": self.find_caption(nearby_text),
                    "nearby_text": nearby_text
                })

        doc.close()
        return self.metadata

    def save_metadata(self, output_path):
        with open(output_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)




 
